"""
订单 Schema
"""
from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional


class CreateOrderRequest(BaseModel):
    """创建订单"""
    product_type: str = Field(..., description="org_plan | personal_plan | once_package | template")
    product_id: Optional[str] = Field(None, description="产品SKU")
    org_id: Optional[int] = None


class OrderResponse(BaseModel):
    """订单响应"""
    id: int
    order_no: str
    product_type: str
    product_name: str
    amount: float
    pay_status: str
    created_at: str

    # 微信支付参数
    wx_pay_params: Optional[dict] = None

    class Config:
        from_attributes = True


class PlanInfo(BaseModel):
    """套餐信息"""
    plan_code: str
    plan_name: str
    price: float
    original_price: float
    features: list[str]
    monthly_quota: int
    teacher_limit: int
    resolution: str
    recommended: bool = False
