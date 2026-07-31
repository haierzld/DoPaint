"""
机构管理接口（园长/管理员）
GET    /api/v1/organizations/info            - 机构信息
PUT    /api/v1/organizations/info            - 更新机构信息
GET    /api/v1/organizations/teachers        - 教师列表
POST   /api/v1/organizations/teachers        - 添加教师
DELETE /api/v1/organizations/teachers/{id}   - 移除教师
GET    /api/v1/organizations/usage           - 用量统计
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user, get_current_org_admin
from app.schemas.organization import OrganizationUpdate
from app.models.user import User
from app.models.organization import Organization
from app.models.artwork import Artwork
from app.models.animation import Animation
from app.utils.response import success, paginated, error

router = APIRouter()


@router.get("/info", summary="机构信息")
async def get_org_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取当前用户的机构信息"""
    if not current_user.org_id:
        return error("未加入任何机构")

    org = db.query(Organization).filter(Organization.id == current_user.org_id).first()
    if not org:
        return error("机构不存在")

    teacher_count = (
        db.query(User).filter(User.org_id == org.id, User.status == 1).count()
    )

    return success(
        data={
            "id": org.id,
            "name": org.name,
            "logo": org.logo,
            "province": org.province,
            "city": org.city,
            "district": org.district,
            "address": org.address,
            "contact_name": org.contact_name,
            "contact_phone": org.contact_phone,
            "plan_type": org.plan_type,
            "monthly_quota": org.monthly_quota,
            "used_quota": org.used_quota,
            "plan_start_at": org.plan_start_at.isoformat() if org.plan_start_at else "",
            "plan_expire_at": org.plan_expire_at.isoformat() if org.plan_expire_at else "",
            "teacher_count": teacher_count,
            "status": org.status,
        }
    )


@router.put("/info", summary="更新机构信息")
async def update_org_info(
    data: OrganizationUpdate,
    current_user: User = Depends(get_current_org_admin),
    db: Session = Depends(get_db),
):
    """更新机构基本信息（仅园长/管理员）"""
    org = db.query(Organization).filter(Organization.id == current_user.org_id).first()
    if not org:
        return error("机构不存在")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(org, key, value)

    db.commit()
    return success(message="更新成功")


@router.get("/teachers", summary="教师列表")
async def list_teachers(
    page: int = 1,
    page_size: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取机构下教师列表"""
    if not current_user.org_id:
        return error("未加入任何机构")

    query = db.query(User).filter(
        User.org_id == current_user.org_id, User.status == 1
    )
    total = query.count()
    users = (
        query.order_by(User.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    items = [
        {
            "id": u.id,
            "nickname": u.nickname or "",
            "avatar": u.avatar or "",
            "phone": u.phone or "",
            "role": u.role,
            "status": u.status,
            "created_at": u.created_at.isoformat() if u.created_at else "",
        }
        for u in users
    ]

    return paginated(items=items, total=total, page=page, page_size=page_size)


@router.post("/teachers", summary="添加教师")
async def add_teacher(
    user_id: int,
    current_user: User = Depends(get_current_org_admin),
    db: Session = Depends(get_db),
):
    """将已有用户加入机构（仅园长/管理员）"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return error("用户不存在")

    if user.org_id:
        return error("该用户已加入其他机构")

    user.org_id = current_user.org_id
    user.role = "teacher"
    db.commit()

    return success(message="添加成功")


@router.delete("/teachers/{user_id}", summary="移除教师")
async def remove_teacher(
    user_id: int,
    current_user: User = Depends(get_current_org_admin),
    db: Session = Depends(get_db),
):
    """从机构移除教师"""
    user = db.query(User).filter(
        User.id == user_id, User.org_id == current_user.org_id
    ).first()
    if not user:
        return error("教师不存在或不在本机构")

    if user.role == "admin":
        return error("不能移除园长")

    user.org_id = None
    user.role = "individual"
    db.commit()

    return success(message="已移除")


@router.get("/usage", summary="用量统计")
async def get_usage_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取机构本月用量统计"""
    if not current_user.org_id:
        return error("未加入任何机构")

    org = db.query(Organization).filter(Organization.id == current_user.org_id).first()

    # 本月动画数
    from datetime import datetime
    now = datetime.utcnow()
    month_start = now.replace(day=1, hour=0, minute=0, second=0)

    total_animations = (
        db.query(Animation)
        .filter(
            Animation.org_id == current_user.org_id,
            Animation.created_at >= month_start,
        )
        .count()
    )
    completed = (
        db.query(Animation)
        .filter(
            Animation.org_id == current_user.org_id,
            Animation.created_at >= month_start,
            Animation.status == "completed",
        )
        .count()
    )
    total_artworks = (
        db.query(Artwork)
        .filter(
            Artwork.org_id == current_user.org_id,
            Artwork.created_at >= month_start,
        )
        .count()
    )

    return success(
        data={
            "monthly_quota": org.monthly_quota if org else 0,
            "used_quota": org.used_quota if org else 0,
            "remaining": (org.monthly_quota - org.used_quota) if org else 0,
            "total_animations": total_animations,
            "completed_animations": completed,
            "total_artworks": total_artworks,
            "month": now.strftime("%Y-%m"),
        }
    )
