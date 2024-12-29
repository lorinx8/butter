from typing import Any, Optional, TypeVar, Generic
from pydantic import BaseModel
from app.core.exceptions.error_code import ErrorCode

T = TypeVar('T')


class ResponseModel(BaseModel, Generic[T]):
    code: int = ErrorCode.SUCCESS.value
    message: str = "Success"
    data: Optional[T] = None


def success_response(data: Any = None, message: str = "Success") -> dict:
    return ResponseModel(
        code=ErrorCode.SUCCESS.value,
        message=message,
        data=data
    ).model_dump()


def error_response(error_code: ErrorCode, message: str = None) -> dict:
    if message is None:
        message = error_code.name
    return ResponseModel(
        code=error_code.value,
        message=message,
        data=None
    ).model_dump()
