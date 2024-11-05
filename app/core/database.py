from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# 创建同步引擎
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # 添加连接池健康检查
    pool_size=5,  # 连接池大小
    max_overflow=10  # 最大溢出连接数
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 