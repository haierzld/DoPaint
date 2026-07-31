"""
认证相关 Schema
"""
from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field


class WechatLoginRequest(BaseModel):
    """微信小程序登录请求"""
    code: str = Field(..., description="微信临时登录凭证 code")


class LoginResponse(BaseModel):
    """登录响应"""
    access_token: str = Field(..., description="JWT Token")
    token_type: str = "bearer"
    user_id: int
    nickname: str
    avatar: str = ""
    role: str
    org_id: int | None = None
    org_name: str = ""
    plan_type: str = "free"


class UserProfile(BaseModel):
    """用户信息"""
    id: int
    nickname: str
    avatar: str
    phone: str = ""
    role: str
    org_id: int | None
    org_name: str = ""
    plan_type: str
    monthly_quota: int
    used_quota: int
    remaining_quota: int
    plan_expire_at: str = ""
    created_at: str

    class Config:
        from_attributes = True
