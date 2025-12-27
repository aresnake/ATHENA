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
