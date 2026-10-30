# backend/app/utils/response.py
from typing import Any, Optional, Dict
from flask import jsonify

def success_response(
    data: Any = None,
    message: str = "Operation successful",
    status_code: int = 200,
    meta: Optional[Dict[str, Any]] = None
):
    payload = {
        "success": True,
        "message": message,
        "data": data if data is not None else {},
        "meta": meta if meta is not None else {}
    }
    return jsonify(payload), status_code

def error_response(
    message: str = "An error occurred",
    error_code: str = "INTERNAL_ERROR",
    status_code: int = 400,
    details: Optional[Dict[str, Any]] = None
):
    payload = {
        "success": False,
        "message": message,
        "error_code": error_code,
        "details": details if details is not None else {}
    }
    return jsonify(payload), status_code
