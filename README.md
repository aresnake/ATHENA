# Athena MCP + Blender Bridge

Minimal MCP server with HTTP + stdio transports and a Blender HTTP bridge. Tool implementations are routed through a bridge client and are safe to import without Blender.

## Setup
- Create/activate the virtual environment (already present as `.venv`): `.\.venv\Scripts\Activate.ps1`
- Install test extras: `pip install .[test]`

## Run the MCP server
- HTTP transport: `python -m athena_mcp.mcp_core.server --http --host 127.0.0.1 --port 9000`
- Stdio transport: `python -m athena_mcp.mcp_core.server --stdio`
- Both transports: `python -m athena_mcp.mcp_core.server --http --stdio`
- The server expects the Blender bridge on `127.0.0.1:8765` by default; override with `--bridge-host/--bridge-port`.

## Run the Blender bridge
- Headless: `blender.exe --factory-startup --background --python src/athena_mcp/blender_bridge/provider_http.py`
- UI session: `blender.exe --factory-startup --python src/athena_mcp/blender_bridge/provider_http.py`
- The bridge hosts `http://127.0.0.1:8765` with `/health` and `/exec` endpoints and executes requests on Blender's main thread via a timer + queue. The HTTP server runs in a background daemon thread so the Blender UI stays responsive; requests wait briefly for results and return a timeout error if the main thread does not complete in time.

## Bridge URL
- MCP calls forward to the Blender bridge at `ATHENA_BRIDGE_URL` (default `http://127.0.0.1:8765`). Override per-process: `set ATHENA_BRIDGE_URL=http://127.0.0.1:9876` before starting the MCP server.

## Verify with PowerShell
```powershell
Invoke-RestMethod -Method Get http://127.0.0.1:9000/health
Invoke-RestMethod -Method Get http://127.0.0.1:9000/tools/list
Invoke-RestMethod -Method Post http://127.0.0.1:9000/tools/call -Body '{"name":"blender-list-objects","args":{}}' -ContentType 'application/json'
# Sample responses (flattened):
# { "ok": true, "result": { "objects": ["Cube"], "count": 1 } }
# { "ok": true, "result": { "name": "Cube", "location": [0,0,0], "size": 1.0 } }
```

## Live modeling script (example sequence)
1. Add a cube: `{"name":"blender-add-cube","args":{"name":"Cube"}}`
2. Enter edit mode: `{"name":"blender-set-mode","args":{"mode":"EDIT","name":"Cube"}}`
3. Select all: `{"name":"blender-select-all","args":{}}`
4. Bevel edges: `{"name":"blender-mesh-bevel","args":{"offset":0.02,"segments":1}}`
5. Add loop cut: `{"name":"blender-mesh-loop-cut","args":{"cuts":1}}`
6. Inset faces: `{"name":"blender-mesh-inset","args":{"thickness":0.05,"depth":0.0}}`
7. Extrude up: `{"name":"blender-mesh-extrude","args":{"x":0,"y":0,"z":1}}`
8. Return to object mode: `{"name":"blender-set-mode","args":{"mode":"OBJECT","name":"Cube"}}`

## Pack 03 selection (example chain)
- Set edit mode: `{"name":"blender-set-mode","args":{"mode":"EDIT","name":"Cube"}}`
- Switch to edge selection: `{"name":"blender-set-selection-mode","args":{"mode":"EDGE"}}`
- Select loop (extend): `{"name":"blender-mesh-select-loop","args":{"extend":true}}`
- Bevel or extrude after selection as desired.

## Tests
- Run `python -m pytest` (no Blender required). Tests cover tool listing, tool call routing with a mocked bridge, and an HTTP server health smoke test.

## Audit
- Execute `powershell -File tools/audit.ps1` to print git status, Python version, pytest run, port checks, and example REST commands.

## Troubleshooting
- Port 9000 or 8765 in use: stop the conflicting process (`netstat -ano | findstr ":9000"`), or choose alternate ports via `--port` / `--bridge-port`.
- MCP server cannot reach Blender bridge: confirm the bridge process is running and reachable at `127.0.0.1:8765` (check `/health`).
- Blender operations fail: ensure the bridge is started with `--factory-startup` to avoid add-ons interfering, and that tool payloads match the documented schemas.
- Running the bridge script directly in Blender: the bridge is self-contained and adjusts `sys.path` so you can pass the absolute path to `provider_http.py` without installing `athena_mcp`.
- UI still freezes: confirm you're using the provided `provider_http.py` which starts its HTTP server on a background thread; timeouts in `/exec` responses indicate the main-thread queue isn't processing quickly enough (ensure the timer is running and the scene isn't blocked by modal operations).
