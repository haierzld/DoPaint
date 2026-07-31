"""
提示词模板 Schema
"""
from __future__ import annotations
from pydantic import BaseModel
from typing import Optional


class PromptTemplateResponse(BaseModel):
    """提示词模板响应"""
    id: int
    style_code: str
    style_name: str
    style_icon: Optional[str]
    description: Optional[str]
    category: Optional[str]
    default_duration: int
    default_resolution: str
    thumbnail: Optional[str]
    demo_video_url: Optional[str]
    is_preset: bool
    is_paid: bool
    price: float
    required_plan: Optional[str]
    sort_order: int

    class Config:
        from_attributes = True


class PromptTemplateListResponse(BaseModel):
    """提示词模板列表"""
    total: int
    items: list[PromptTemplateResponse]
