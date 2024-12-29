from app.core.exceptions.error_code import ErrorCode


class ButterException(Exception):
    """业务异常基类"""

    def __init__(
        self,
        code: ErrorCode,
        message: str,
    ):
        self.code = code
        self.message = message
        super().__init__(self.message)
