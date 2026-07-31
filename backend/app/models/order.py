"""
订单模型
"""
from sqlalchemy import Column, String, Integer, BigInteger, Float, DateTime, Enum as SqlEnum
from app.models.base import BaseModel


class Order(BaseModel):
    """订单表"""

    __tablename__ = "orders"

    order_no = Column(String(32), unique=True, nullable=False, comment="订单号")
    org_id = Column(BigInteger, index=True, comment="机构ID")
    user_id = Column(BigInteger, index=True, comment="用户ID")

    # 商品信息
    product_type = Column(
        SqlEnum("org_plan", "personal_plan", "once_package", "template", "custom"),
        nullable=False,
        comment="商品类型",
    )
    product_id = Column(String(50), comment="产品SKU")
    product_name = Column(String(200), comment="产品名称")

    # 金额
    amount = Column(Float, nullable=False, comment="金额(元)")
    discount_amount = Column(Float, default=0, comment="优惠金额")

    # 支付
    pay_status = Column(
        SqlEnum("pending", "paid", "refunding", "refunded", "cancelled"),
        default="pending",
        comment="支付状态",
    )
    pay_method = Column(String(50), comment="支付方式")
    pay_time = Column(DateTime, comment="支付时间")
    wx_transaction_id = Column(String(100), comment="微信支付交易号")

    # 退款
    refund_amount = Column(Float, default=0, comment="退款金额")
    refund_time = Column(DateTime, comment="退款时间")
