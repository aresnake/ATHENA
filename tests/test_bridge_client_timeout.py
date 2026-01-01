import importlib

from athena_mcp.mcp_core import bridge_client


def _reload_with_env(monkeypatch, env_value=None):
    """Reload bridge_client with optional timeout override."""
    monkeypatch.delenv("ATHENA_BRIDGE_TIMEOUT", raising=False)
    monkeypatch.delenv("ATHENA_BLENDER_BRIDGE_TIMEOUT", raising=False)
    if env_value is not None:
        monkeypatch.setenv("ATHENA_BRIDGE_TIMEOUT", env_value)
    return importlib.reload(bridge_client)


class DummyResponse:
    status = 200

    def read(self):
        return b'{"ok": true, "result": {"ping": "pong"}}'


class DummyConnection:
    last_timeout = None

    def __init__(self, _host, _port, timeout):
        DummyConnection.last_timeout = timeout

    def request(self, *args, **kwargs):
        return None

    def getresponse(self):
        return DummyResponse()

    def close(self):
        return None


def test_bridge_timeout_defaults_to_generous_value(monkeypatch):
    module = _reload_with_env(monkeypatch, None)
    monkeypatch.setattr(module.http.client, "HTTPConnection", DummyConnection)

    result = module.bridge_request("test-tool", {})

    assert result["ok"] is True
    assert DummyConnection.last_timeout == module._DEFAULT_TIMEOUT
    assert DummyConnection.last_timeout >= module._BRIDGE_WAIT_TIMEOUT + module._CLIENT_TIMEOUT_MARGIN


def test_bridge_timeout_respects_env_override(monkeypatch):
    module = _reload_with_env(monkeypatch, "12.5")
    monkeypatch.setattr(module.http.client, "HTTPConnection", DummyConnection)

    _ = module.bridge_request("test-tool", {})

    assert DummyConnection.last_timeout == module._BRIDGE_WAIT_TIMEOUT + module._CLIENT_TIMEOUT_MARGIN


def test_bridge_timeout_can_be_overridden_per_call(monkeypatch):
    module = _reload_with_env(monkeypatch, "45")
    monkeypatch.setattr(module.http.client, "HTTPConnection", DummyConnection)

    _ = module.bridge_request("test-tool", {}, timeout=2.5)

    assert DummyConnection.last_timeout == module._BRIDGE_WAIT_TIMEOUT + module._CLIENT_TIMEOUT_MARGIN
