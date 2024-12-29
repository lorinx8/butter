from enum import Enum


class ErrorCode(Enum):
    SUCCESS = (0, "Success")

    # 通用错误 (1000-1999)
    UNKNOWN_ERROR = (1000, "Unknown error")
    INVALID_PARAMS = (1001, "Invalid parameters")
    UNAUTHORIZED = (1002, "Unauthorized")
    FORBIDDEN = (1003, "Forbidden")
    NOT_FOUND = (1004, "Not found")

    # 用户相关错误 (2000-2999)
    USER_NOT_FOUND = (2000, "User not found")
    USER_ALREADY_EXISTS = (2001, "User already exists")
    INVALID_PASSWORD = (2002, "Invalid password")
    LOGIN_FAILED = (2003, "Login failed")

    # 模型相关错误 (4000-4999)
    MODEL_NOT_FOUND = (4000, "Model not found")
    MODEL_ALREADY_EXISTS = (4001, "Model already exists")
    MODEL_MANAGER_NOT_INITIALIZED = (4002, "Model manager not initialized")

    # 机器人业务相关错误
    BOT_NOT_FOUND = (5000, "Bot not found")
    BOT_ALREADY_EXISTS = (5001, "Bot already exists")
    BOT_MANAGER_NOT_INITIALIZED = (5002, "Bot manager not initialized")

    # 数据库相关错误 (3000-3999)
    DB_ERROR = (3000, "Database error")

    # 系统错误 (9500-9599)
    INTERNAL_SERVER_ERROR = (9500, "Internal server error")

    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
