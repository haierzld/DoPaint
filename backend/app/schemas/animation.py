"""
动画相关 Schema
"""
from __future__ import annotations
from pydantic import BaseModel, Field, field_validator
from typing import Optional


class AnimationGenerateRequest(BaseModel):
    """生成动画请求"""
    artwork_id: int = Field(..., description="画作ID")
    style_code: str = Field(..., description="风格编号")
    custom_prompt: Optional[str] = Field(None, max_length=500, description="自定义提示词")
    duration: int = Field(5, ge=3, le=10, description="视频时长(秒)")
    resolution: str = Field("720p", description="分辨率")

    @field_validator("resolution")
    @classmethod
    def check_resolution(cls, v):
        allowed = ["480p", "720p", "1080p"]
        if v not in allowed:
            raise ValueError(f"分辨率必须是 {allowed} 之一")
        return v


class AnimationBatchRequest(BaseModel):
    """批量生成请求"""
    artwork_ids: list[int] = Field(..., min_length=1, max_length=30, description="画作ID列表")
    style_code: str = Field(..., description="风格编号")
    custom_prompt: Optional[str] = Field(None, max_length=500)
    duration: int = Field(5, ge=3, le=8)
    resolution: str = Field("720p")

    @field_validator("resolution")
    @classmethod
    def check_resolution(cls, v):
        allowed = ["480p", "720p", "1080p"]
        if v not in allowed:
            raise ValueError(f"分辨率必须是 {allowed} 之一")
        return v


class AnimationGenerateResponse(BaseModel):
    """生成动画响应"""
    animation_id: int
    artwork_id: int
    status: str
    estimated_seconds: int = 30


class AnimationStatusResponse(BaseModel):
    """动画状态响应"""
    animation_id: int
    artwork_id: int
    status: str  # queued | generating | completed | failed
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    duration: int = 5
    resolution: str = "720p"
    prompt_style: str
    error_msg: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None
    estimated_seconds: Optional[int] = None

    class Config:
        from_attributes = True


class AnimationListResponse(BaseModel):
    """动画列表项"""
    id: int
    artwork_id: int
    artwork_title: Optional[str] = None
    artwork_thumbnail: Optional[str] = None
    author_name: Optional[str] = None
    prompt_style: str
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    duration: int
    status: str
    created_at: str

    class Config:
        from_attributes = True
