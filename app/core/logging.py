import sys
from pathlib import Path
from loguru import logger

def setup_logging():
    # 移除默认的处理器
    logger.remove()
    
    # 添加控制台输出
    logger.add(
        sys.stdout,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        level="INFO"
    )
    
    # 添加文件日志
    log_file_path = Path("logs/app.log")
    log_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    logger.add(
        log_file_path,
        rotation="500 MB",
        retention="10 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        level="DEBUG"
    )

    return logger 