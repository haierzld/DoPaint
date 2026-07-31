"""
依赖注入模块
- 数据库会话
- 当前用户获取
- 配额检查
"""
from typing import Generator, Optional
from fastapi import Depends, HTTPException, Header, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import decode_access_token
from app.models.base import SessionLocal


# ==================== 数据库会话 ====================

def get_db() -> Generator[Session, None, None]:
    """获取数据库会话（请求结束自动关闭）"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==================== 当前用户 ====================

async def get_current_user(
    authorization: str = Header(..., description="Bearer {token}"),
    db: Session = Depends(get_db),
):
    """从 JWT Token 中解析当前用户"""
    from app.models.user import User  # 延迟导入避免循环引用

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="认证格式错误，请使用 Bearer Token",
        )

    token = authorization.replace("Bearer ", "")
    payload = decode_access_token(token)
    user_id: int = payload.get("user_id")

    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token 无效")

    user = db.query(User).filter(User.id == user_id, User.status == 1).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在或已禁用")

    return user


async def get_current_org_admin(
    current_user=Depends(get_current_user),
):
    """要求当前用户是园长/管理员角色"""
    if current_user.role not in ("admin",):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="仅园长/管理员可操作",
        )
    return current_user


# ==================== 配额检查 ====================

async def check_quota(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """检查用户是否还有可用配额"""
    from app.services.quota_service import QuotaService

    quota = QuotaService(db)
    remaining = quota.get_remaining(current_user)

    if remaining <= 0:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="本月生成配额已用完，请升级套餐或等待下月重置",
        )
    return current_user
