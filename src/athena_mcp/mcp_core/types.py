from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Protocol, TypedDict


JSONDict = Dict[str, Any]


class BridgeFunc(Protocol):
    def __call__(self, tool: str, args: JSONDict) -> JSONDict:
        ...


class ErrorPayload(TypedDict):
    message: str
    code: str


def ok_response(**payload: Any) -> JSONDict:
    return {"ok": True, **payload}


def error_response(message: str, code: str = "error", **extra: Any) -> JSONDict:
    data: JSONDict = {"ok": False, "error": {"message": message, "code": code}}
    if extra:
        data["error"].update(extra)
    return data


def jsonrpc_result(request_id: Any, result: Any) -> JSONDict:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def jsonrpc_error(request_id: Any, code: int, message: str, data: Any | None = None) -> JSONDict:
    error: JSONDict = {"code": code, "message": message}
    if data is not None:
        error["data"] = data
    return {"jsonrpc": "2.0", "id": request_id, "error": error}


@dataclass
class ToolDefinition:
    name: str
    description: str
    input_schema: JSONDict
    impl: Callable[[JSONDict], JSONDict]

    def to_wire(self) -> JSONDict:
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
        }
