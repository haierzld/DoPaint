"""
机构相关 Schema
"""
from pydantic import BaseModel, Field
from typing import Optional


class OrganizationInfo(BaseModel):
    """机构基本信息"""
    id: int
    name: str
    logo: Optional[str]
    province: Optional[str]
    city: Optional[str]
    plan_type: str
    monthly_quota: int
    used_quota: int
    plan_expire_at: Optional[str]
    teacher_count: int = 0

    class Config:
        from_attributes = True


class OrganizationUpdate(BaseModel):
    """更新机构信息"""
    name: Optional[str] = Field(None, max_length=200)
    logo: Optional[str] = None
    province: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    address: Optional[str] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None


class TeacherManage(BaseModel):
    """教师管理"""
    user_id: int


class TeacherListResponse(BaseModel):
    """教师列表项"""
    id: int
    nickname: str
    avatar: Optional[str]
    phone: Optional[str]
    role: str
    status: int
    created_at: str

    class Config:
        from_attributes = True
