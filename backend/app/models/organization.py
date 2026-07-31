"""
组织/机构模型 - 幼儿园
"""
from sqlalchemy import Column, String, Integer, DateTime, Enum as SqlEnum, Text
from app.models.base import BaseModel


class Organization(BaseModel):
    """幼儿园/机构"""

    __tablename__ = "organizations"

    name = Column(String(200), nullable=False, comment="幼儿园名称")
    logo = Column(String(500), comment="Logo URL")
    province = Column(String(50), comment="省份")
    city = Column(String(50), comment="城市")
    district = Column(String(50), comment="区县")
    address = Column(String(500), comment="详细地址")
    contact_name = Column(String(50), comment="联系人")
    contact_phone = Column(String(20), comment="联系电话")

    # 套餐信息
    plan_type = Column(
        SqlEnum("free", "trial", "basic", "standard", "flagship", "group"),
        default="free",
        comment="套餐类型",
    )
    plan_start_at = Column(DateTime, comment="套餐开始时间")
    plan_expire_at = Column(DateTime, comment="套餐到期时间")
    monthly_quota = Column(Integer, default=5, comment="每月生成配额")
    used_quota = Column(Integer, default=0, comment="当月已用配额")
    quota_reset_at = Column(DateTime, comment="配额重置时间")

    # 状态
    status = Column(Integer, default=1, comment="1-正常 2-试用中 0-禁用")
