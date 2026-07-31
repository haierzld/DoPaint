"""
画作相关 Schema
"""
from pydantic import BaseModel, Field
from typing import Optional


class ArtworkUploadResponse(BaseModel):
    """画作上传响应"""
    id: int
    title: Optional[str]
    author_name: Optional[str]
    original_url: str
    processed_url: Optional[str]
    thumbnail_url: Optional[str]
    source: str
    status: str
    created_at: str

    class Config:
        from_attributes = True


class ArtworkListResponse(BaseModel):
    """画作列表项"""
    id: int
    title: Optional[str]
    author_name: Optional[str]
    thumbnail_url: Optional[str]
    original_url: str
    source: str
    status: str
    created_at: str
    animation_count: int = 0  # 该画作已生成的动画数
    latest_video_url: Optional[str] = None  # 最新动画视频

    class Config:
        from_attributes = True


class ArtworkListQuery(BaseModel):
    """画作列表查询参数"""
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    status: Optional[str] = None
    keyword: Optional[str] = None
    sort_by: str = "created_at"
    sort_order: str = "desc"
