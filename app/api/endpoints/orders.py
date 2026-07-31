"""
订单与支付接口
GET    /api/v1/orders/plans           - 套餐列表
POST   /api/v1/orders/create          - 创建订单
POST   /api/v1/orders/{order_no}/pay  - 发起支付
GET    /api/v1/orders                 - 订单列表
POST   /api/v1/orders/notify          - 微信支付回调
"""
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from loguru import logger

from app.core.deps import get_db, get_current_user
from app.core.config import settings
from app.schemas.order import CreateOrderRequest
from app.models.user import User
from app.models.order import Order
from app.models.organization import Organization
from app.utils.response import success, paginated, error

router = APIRouter()

# ====== 套餐定义 ======
PLANS = [
    {
        "plan_code": "basic",
        "plan_name": "基础版",
        "price": 1999,
        "original_price": 2499,
        "features": [
            "500次/月 生成量",
            "5种动画风格",
            "基础提示词模板",
            "720P 视频下载",
            "5位教师账号",
        ],
        "monthly_quota": 500,
        "teacher_limit": 5,
        "resolution": "720p",
    },
    {
        "plan_code": "standard",
        "plan_name": "标准版",
        "price": 4999,
        "original_price": 5999,
        "features": [
            "1,500次/月 生成量",
            "8种动画风格",
            "高级提示词模板",
            "批量生成（最多30幅）",
            "1080P 视频下载",
            "15位教师账号",
            "班级画廊功能",
            "用量报表",
        ],
        "monthly_quota": 1500,
        "teacher_limit": 15,
        "resolution": "1080p",
        "recommended": True,
    },
    {
        "plan_code": "flagship",
        "plan_name": "旗舰版",
        "price": 9999,
        "original_price": 12999,
        "features": [
            "5,000次/月 生成量",
            "全部动画风格 + 自定义",
            "全部提示词模板",
            "不限教师账号",
            "品牌定制（Logo/主题色）",
            "优先技术支持",
        ],
        "monthly_quota": 5000,
        "teacher_limit": 999,
        "resolution": "1080p",
    },
]

PERSONAL_PLANS = [
    {
        "plan_code": "monthly",
        "plan_name": "个人月卡",
        "price": 29.9,
        "original_price": 39.9,
        "features": ["100次/月", "6种风格", "去水印"],
        "monthly_quota": 100,
        "teacher_limit": 1,
        "resolution": "720p",
    },
    {
        "plan_code": "quarterly",
        "plan_name": "个人季卡",
        "price": 69.9,
        "original_price": 99.9,
        "features": ["400次/季", "全部风格", "去水印"],
        "monthly_quota": 400,
        "teacher_limit": 1,
        "resolution": "720p",
    },
    {
        "plan_code": "yearly",
        "plan_name": "个人年卡",
        "price": 199,
        "original_price": 299,
        "features": ["2000次/年", "全部风格", "去水印", "优先处理"],
        "monthly_quota": 2000,
        "teacher_limit": 1,
        "resolution": "1080p",
    },
]


@router.get("/plans", summary="套餐列表")
async def list_plans():
    """获取所有可购买套餐"""
    return success(
        data={
            "org_plans": PLANS,
            "personal_plans": PERSONAL_PLANS,
        }
    )


@router.post("/create", summary="创建订单")
async def create_order(
    req: CreateOrderRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """创建支付订单"""
    order_no = datetime.utcnow().strftime("%Y%m%d%H%M%S") + uuid.uuid4().hex[:8].upper()

    # 查找产品
    product_name = ""
    amount = 0
    all_plans = PLANS + PERSONAL_PLANS
    for plan in all_plans:
        if plan["plan_code"] == req.product_id:
            product_name = plan["plan_name"]
            amount = plan["price"]
            break

    if amount <= 0:
        return error("产品不存在")

    order = Order(
        order_no=order_no,
        org_id=req.org_id or current_user.org_id,
        user_id=current_user.id,
        product_type=req.product_type,
        product_id=req.product_id,
        product_name=product_name,
        amount=amount,
        pay_status="pending",
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    return success(
        data={
            "id": order.id,
            "order_no": order.order_no,
            "product_type": order.product_type,
            "product_name": order.product_name,
            "amount": order.amount,
            "pay_status": order.pay_status,
            "created_at": order.created_at.isoformat() if order.created_at else "",
        }
    )


@router.post("/{order_no}/pay", summary="发起微信支付")
async def pay_order(
    order_no: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    发起微信支付，返回小程序调起支付所需参数

    实际开发中需调用微信支付 API：
    https://pay.weixin.qq.com/doc/v3/merchant/4012062626
    """
    order = db.query(Order).filter(Order.order_no == order_no).first()
    if not order:
        return error("订单不存在")

    if order.pay_status != "pending":
        return error("订单状态异常")

    # TODO: 调用微信支付统一下单 API
    # wx_pay_params = wechat_pay_service.unified_order(order)
    # 此处返回模拟数据
    wx_pay_params = {
        "appId": settings.WECHAT_APP_ID,
        "timeStamp": str(int(datetime.utcnow().timestamp())),
        "nonceStr": uuid.uuid4().hex[:16],
        "package": f"prepay_id=wx_prepay_{order_no}",
        "signType": "RSA",
        "paySign": "mock_signature",
    }

    return success(
        data={
            "order_no": order.order_no,
            "amount": order.amount,
            "product_name": order.product_name,
            "wx_pay_params": wx_pay_params,
        }
    )


@router.get("", summary="订单列表")
async def list_orders(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """查询当前用户的订单列表"""
    query = db.query(Order).filter(Order.user_id == current_user.id)

    total = query.count()
    orders = (
        query.order_by(Order.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    items = [
        {
            "id": o.id,
            "order_no": o.order_no,
            "product_type": o.product_type,
            "product_name": o.product_name,
            "amount": o.amount,
            "pay_status": o.pay_status,
            "pay_time": o.pay_time.isoformat() if o.pay_time else None,
            "created_at": o.created_at.isoformat() if o.created_at else "",
        }
        for o in orders
    ]

    return paginated(items=items, total=total, page=page, page_size=page_size)


@router.post("/notify", summary="微信支付回调")
async def payment_notify(request: Request, db: Session = Depends(get_db)):
    """
    微信支付结果通知回调

    微信支付完成后会 POST 到此接口，需验证签名后处理
    """
    body = await request.body()

    # TODO: 解密并验证支付通知
    # result = wechat_pay_service.decrypt_notify(body)
    # 此处模拟处理
    logger.info(f"收到支付回调: {len(body)} bytes")

    # 更新订单状态
    # order = db.query(Order).filter(Order.order_no == result["out_trade_no"]).first()
    # order.pay_status = "paid"
    # order.wx_transaction_id = result["transaction_id"]
    # order.pay_time = datetime.utcnow()

    # 激活套餐
    # org = db.query(Organization).filter(Organization.id == order.org_id).first()
    # org.plan_type = order.product_id
    # org.plan_start_at = datetime.utcnow()
    # org.plan_expire_at = datetime.utcnow() + timedelta(days=365)
    # org.monthly_quota = PLAN_QUOTA[order.product_id]
    # db.commit()

    return {"code": "SUCCESS", "message": "OK"}
