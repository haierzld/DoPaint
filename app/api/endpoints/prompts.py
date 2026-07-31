"""
提示词模板接口
GET  /api/v1/prompts                - 获取可用模板列表
GET  /api/v1/prompts/{style_code}   - 模板详情
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.models.prompt_template import PromptTemplate
from app.models.user import User
from app.utils.response import success

router = APIRouter()


@router.get("", summary="获取可用提示词模板")
async def list_prompts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取当前用户在套餐权限内可用的提示词模板列表"""
    templates = (
        db.query(PromptTemplate)
        .filter(PromptTemplate.status == 1)
        .order_by(PromptTemplate.sort_order)
        .all()
    )

    items = []
    for t in templates:
        items.append({
            "id": t.id,
            "style_code": t.style_code,
            "style_name": t.style_name,
            "style_icon": t.style_icon,
            "description": t.description,
            "system_prompt": t.system_prompt,
            "negative_prompt": t.negative_prompt,
            "category": t.category,
            "default_duration": t.default_duration,
            "default_resolution": t.default_resolution,
            "thumbnail": t.thumbnail,
            "demo_video_url": t.demo_video_url,
            "is_preset": t.is_preset,
            "is_paid": t.is_paid,
            "price": t.price,
            "required_plan": t.required_plan,
            "sort_order": t.sort_order,
        })

    return success(data={"total": len(items), "items": items})


@router.get("/{style_code}", summary="模板详情")
async def get_prompt_detail(
    style_code: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取指定提示词模板详情"""
    template = (
        db.query(PromptTemplate)
        .filter(PromptTemplate.style_code == style_code, PromptTemplate.status == 1)
        .first()
    )
    if not template:
        return success(data=None, message="模板不存在")

    return success(
        data={
            "id": template.id,
            "style_code": template.style_code,
            "style_name": template.style_name,
            "style_icon": template.style_icon,
            "description": template.description,
            "system_prompt": template.system_prompt,
            "negative_prompt": template.negative_prompt,
            "category": template.category,
            "default_duration": template.default_duration,
            "default_resolution": template.default_resolution,
            "thumbnail": template.thumbnail,
            "demo_video_url": template.demo_video_url,
            "is_preset": template.is_preset,
            "is_paid": template.is_paid,
            "price": template.price,
            "required_plan": template.required_plan,
        }
    )
