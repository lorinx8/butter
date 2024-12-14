from fastapi import Request
import time
from app.core.logging import access_logger
import json
from typing import Callable

async def log_request_body(request: Request) -> str:
    try:
        body = await request.body()
        if body:
            return json.loads(body)
    except:
        pass
    return ""

async def access_log_middleware(request: Request, call_next: Callable):
    # 记录请求开始时间
    start_time = time.time()
    
    # 获取请求体
    body = await log_request_body(request)
    
    response = await call_next(request)
    
    # 计算处理时间
    process_time = (time.time() - start_time) * 1000
    
    # 格式化日志信息
    log_entry = f"{time.strftime('%Y-%m-%d %H:%M:%S')} " \
                f"{request.client.host} " \
                f"{request.method} " \
                f"{request.url.path} " \
                f"{json.dumps(body) if body else '-'} " \
                f"{process_time:.4f}ms " \
                f"{response.status_code}"
    
    # 记录访问日志
    access_logger.info(log_entry)
    
    return response 