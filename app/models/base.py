"""
数据库基础模型
"""
from sqlalchemy import create_engine, Column, Integer, DateTime, func
from sqlalchemy.orm import sessionmaker, declarative_base, declared_attr

from app.core.config import settings

# 引擎（SQLite 和 MySQL 使用不同的连接参数）
_is_sqlite = "sqlite" in settings.DATABASE_URL

if _is_sqlite:
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=settings.APP_DEBUG,
    )
else:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_size=20,
        max_overflow=40,
        echo=settings.APP_DEBUG,
    )

# 会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 基类
Base = declarative_base()


class BaseModel(Base):
    """所有模型的基类，提供通用字段"""
    __abstract__ = True

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间"
    )
