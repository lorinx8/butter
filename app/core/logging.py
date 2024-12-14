import sys
from pathlib import Path
from loguru import logger

def setup_logging():
    # 移除默认的处理器
    logger.remove()
    
    # 添加控制台输出 (添加过滤器，只输出非访问日志)
    logger.add(
        sys.stdout,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        level="INFO",
        filter=lambda record: not record["extra"].get("access_log")
    )
    
    # 添加应用日志
    log_file_path = Path("logs/app.log")
    log_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    logger.add(
        log_file_path,
        rotation="500 MB",
        retention="10 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        level="DEBUG",
        filter=lambda record: not record["extra"].get("access_log")
    )

    # 添加访问日志
    access_log_path = Path("logs/access.log")
    logger.add(
        access_log_path,
        rotation="500 MB",
        retention="10 days",
        format="{message}",
        filter=lambda record: record["extra"].get("access_log") is True,
        level="INFO"
    )

    return logger

# 创建访问日志记录器
access_logger = logger.bind(access_log=True)