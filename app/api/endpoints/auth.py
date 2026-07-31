"""
认证接口
POST /api/v1/auth/login     - 微信登录
GET  /api/v1/auth/profile   - 获取个人信息
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from loguru import logger

from app.core.deps import get_db, get_current_user
from app.core.security import create_access_token, wechat_code2session
from app.schemas.auth import WechatLoginRequest, LoginResponse, UserProfile
from app.models.user import User
from app.models.organization import Organization
from app.services.quota_service import QuotaService
from app.utils.response import success

router = APIRouter()


@router.post("/login", summary="微信小程序登录")
async def wechat_login(req: WechatLoginRequest, db: Session = Depends(get_db)):
    """
    微信小程序登录流程：
    1. 用临时 code 换取 openid
    2. 查找或创建用户
    3. 返回 JWT Token
    """
    # 换取 openid
    wx_data = await wechat_code2session(req.code)
    openid = wx_data["openid"]

    # 查找或创建用户
    user = db.query(User).filter(User.wechat_openid == openid).first()

    if not user:
        user = User(
            wechat_openid=openid,
            wechat_unionid=wx_data.get("unionid"),
            nickname="新用户",
            role="individual",
            personal_quota=5,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"新用户注册: openid={openid[:10]}...")

    # 生成 Token
    token = create_access_token(data={"user_id": user.id, "openid": openid})

    # 获取机构信息
    org_name = ""
    plan_type = "free"
    if user.org_id:
        org = db.query(Organization).filter(Organization.id == user.org_id).first()
        if org:
            org_name = org.name
            plan_type = org.plan_type

    return success(
        data={
            "access_token": token,
            "token_type": "bearer",
            "user_id": user.id,
            "nickname": user.nickname or "",
            "avatar": user.avatar or "",
            "role": user.role,
            "org_id": user.org_id,
            "org_name": org_name,
            "plan_type": plan_type,
        }
    )


@router.get("/profile", summary="获取个人信息")
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取当前用户信息和配额"""
    quota_svc = QuotaService(db)
    remaining = quota_svc.get_remaining(current_user)

    # 机构信息
    org_name = ""
    plan_type = current_user.personal_plan
    monthly_quota = current_user.personal_quota
    used_quota = current_user.personal_used
    plan_expire_at = ""

    if current_user.org_id:
        org = db.query(Organization).filter(Organization.id == current_user.org_id).first()
        if org:
            org_name = org.name
            plan_type = org.plan_type
            monthly_quota = org.monthly_quota
            used_quota = org.used_quota
            plan_expire_at = org.plan_expire_at.isoformat() if org.plan_expire_at else ""

    return success(
        data={
            "id": current_user.id,
            "nickname": current_user.nickname or "",
            "avatar": current_user.avatar or "",
            "phone": current_user.phone or "",
            "role": current_user.role,
            "org_id": current_user.org_id,
            "org_name": org_name,
            "plan_type": plan_type,
            "monthly_quota": monthly_quota,
            "used_quota": used_quota,
            "remaining_quota": remaining,
            "plan_expire_at": plan_expire_at,
            "created_at": current_user.created_at.isoformat() if current_user.created_at else "",
        }
    )
