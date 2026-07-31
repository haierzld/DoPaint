"""
用户模型 - 教师/园长/个人用户
"""
from sqlalchemy import Column, String, Integer, DateTime, Enum as SqlEnum, BigInteger, ForeignKey
from app.models.base import BaseModel


class User(BaseModel):
    """用户表"""

    __tablename__ = "users"

    org_id = Column(BigInteger, ForeignKey("organizations.id"), nullable=True, comment="所属机构ID")
    wechat_openid = Column(String(100), unique=True, nullable=False, comment="微信OpenID")
    wechat_unionid = Column(String(100), comment="微信UnionID")
    nickname = Column(String(100), comment="昵称")
    avatar = Column(String(500), comment="头像URL")
    phone = Column(String(20), comment="手机号")

    role = Column(
        SqlEnum("admin", "teacher", "individual"),
        default="teacher",
        comment="角色：admin-园长/管理员 teacher-教师 individual-个人用户",
    )

    # 个人套餐（仅 individual 角色，或机构未付费时教师的个人购买）
    personal_plan = Column(
        SqlEnum("free", "monthly", "quarterly", "yearly", "flagship"),
        default="free",
        comment="个人付费计划",
    )
    personal_quota = Column(Integer, default=5, comment="个人月配额")
    personal_used = Column(Integer, default=0, comment="个人当月已用")

    status = Column(Integer, default=1, comment="1-正常 0-禁用")
    last_login_at = Column(DateTime, comment="最后登录时间")
