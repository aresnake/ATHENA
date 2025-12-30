from __future__ import annotations

from typing import Any, Dict

JSONDict = Dict[str, Any]


def ok_response(**payload: Any) -> JSONDict:
    return {"ok": True, **payload}


def error_response(message: str, code: str = "error", **extra: Any) -> JSONDict:
    data: JSONDict = {"ok": False, "error": {"message": message, "code": code}}
    if extra:
        data["error"].update(extra)
    return data
