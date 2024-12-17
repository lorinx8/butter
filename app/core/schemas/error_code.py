from enum import Enum

class ErrorCode(Enum):
    SUCCESS = 0
    
    # 通用错误 (1000-1999)
    UNKNOWN_ERROR = 1000
    INVALID_PARAMS = 1001
    UNAUTHORIZED = 1002
    FORBIDDEN = 1003
    NOT_FOUND = 1004
    
    # 用户相关错误 (2000-2999)
    USER_NOT_FOUND = 2000
    USER_ALREADY_EXISTS = 2001
    INVALID_PASSWORD = 2002
    LOGIN_FAILED = 2003
    
    # 数据库相关错误 (3000-3999)
    DB_ERROR = 3000
    
    # 系统错误 (9500-9599)
    INTERNAL_SERVER_ERROR = 9500
    
    # 其他业务错误可以继续添加...
    MODEL_NOT_FOUND = 10001
    MODEL_ALREADY_EXISTS = 10002