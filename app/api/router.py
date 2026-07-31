"""
路由汇总
"""
from fastapi import APIRouter
from app.api.endpoints import auth, artworks, animations, prompts, organizations, orders

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(artworks.router, prefix="/artworks", tags=["画作"])
api_router.include_router(animations.router, prefix="/animations", tags=["动画"])
api_router.include_router(prompts.router, prefix="/prompts", tags=["提示词模板"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["机构管理"])
api_router.include_router(orders.router, prefix="/orders", tags=["订单支付"])
