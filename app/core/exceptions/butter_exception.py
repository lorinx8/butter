from app.core.schemas.error_code import ErrorCode


class ButterException(Exception):
    """业务异常基类"""
    def __init__(
        self,
        error_code: ErrorCode,
        message: str,
    ):
        self.error_code = error_code
        self.message = message
        super().__init__(self.message)