"""
DoPaint - FastAPI 应用入口
"""
import os
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from loguru import logger

from app.core.config import settings
from app.core.security import create_access_token
from app.models.base import Base, engine, SessionLocal
from app.models.user import User
from app.models.prompt_template import PromptTemplate
from app.api.router import api_router

# 导入所有模型，确保 Base.metadata 包含所有表
import app.models.organization  # noqa
import app.models.user          # noqa
import app.models.artwork       # noqa
import app.models.animation     # noqa
import app.models.prompt_template  # noqa
import app.models.order         # noqa

# 模块级建表（保证 TestClient / uvicorn 启动前表已存在）
Base.metadata.create_all(bind=engine)
logger.info("✅ 数据库表已初始化")


# ==================== 启动/关闭生命周期 ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：初始化种子数据"""
    logger.info("🚀 DoPaint 启动中...")

    # 初始化提示词模板种子数据
    _seed_prompts()
    logger.info("✅ 提示词模板已就绪")

    # 确保 static / local_storage 目录存在
    os.makedirs("local_storage", exist_ok=True)
    os.makedirs("frontend", exist_ok=True)

    yield

    logger.info("👋 DoPaint 已关闭")


def _seed_prompts():
    """初始化提示词种子数据"""
    PROMPTS = [
        {
            "style_code": "magic_fairytale",
            "style_name": "魔法童话",
            "style_icon": "🧚",
            "description": "画面变成温馨童话世界，角色轻轻摆动微笑，星星和闪光飘落",
            "category": "story",
            "system_prompt": "让画面变成一个温馨的魔法童话世界。画面中的角色轻轻摆动、微笑眨眼，周围有闪烁的星星和光点缓缓飘落，整体色调温暖柔和，带有梦幻光晕。保持画作原有的色彩和稚嫩笔触风格。",
            "negative_prompt": "恐怖、暴力、成人内容、画面变形、色彩失真、文字水印",
            "default_duration": 5,
            "is_preset": True,
            "sort_order": 1,
        },
        {
            "style_code": "nature_wonder",
            "style_name": "自然奥秘",
            "style_icon": "🌿",
            "description": "花草生长绽放，蝴蝶翩翩飞舞，小动物探头探脑，四季变化流转",
            "category": "nature",
            "system_prompt": "让画面呈现大自然的生机与美好。花朵缓缓绽放，小草轻轻摇摆，蝴蝶翩翩飞舞，小鸟展翅飞翔，阳光透过树叶洒下温暖光斑。保持画作原有的色彩和稚嫩笔触风格。",
            "negative_prompt": "恐怖、暴力、成人内容、画面变形、色彩失真、文字水印",
            "default_duration": 5,
            "is_preset": True,
            "sort_order": 2,
        },
        {
            "style_code": "festival_celebration",
            "style_name": "节日欢庆",
            "style_icon": "🎉",
            "description": "角色穿上节日盛装，气球彩带飘扬，喜庆热闹的节日氛围",
            "category": "festival",
            "system_prompt": "让画面充满节日喜庆氛围。角色欢快舞动，彩色气球升空飘荡，彩带飞舞，礼花绽放，温暖灯光闪烁，笑脸洋溢。保持画作原有的色彩和稚嫩笔触风格。",
            "negative_prompt": "恐怖、暴力、成人内容、画面变形、色彩失真、文字水印",
            "default_duration": 5,
            "is_preset": True,
            "sort_order": 3,
        },
        {
            "style_code": "ocean_world",
            "style_name": "海底世界",
            "style_icon": "🐟",
            "description": "画面沉入海底，鱼儿游动，珊瑚摇曳，气泡升腾",
            "category": "ocean",
            "system_prompt": "让画面变成神秘美丽的海底世界。彩色的鱼儿自由游动，珊瑚轻轻摇摆，一串串气泡缓缓上升，阳光透过水面洒下蓝色光影。保持画作原有的色彩和稚嫩笔触风格。",
            "negative_prompt": "恐怖、暴力、成人内容、画面变形、色彩失真、文字水印",
            "default_duration": 5,
            "is_preset": True,
            "sort_order": 4,
        },
        {
            "style_code": "space_adventure",
            "style_name": "太空冒险",
            "style_icon": "🚀",
            "description": "画面飞向太空，星星闪烁，行星运转，宇航员漂浮",
            "category": "space",
            "system_prompt": "让画面变成浩瀚神奇的太空。星星闪烁发光，行星缓缓运转，画面中的角色漂浮在星空中，远处有璀璨的银河。保持画作原有的色彩和稚嫩笔触风格。",
            "negative_prompt": "恐怖、暴力、成人内容、画面变形、色彩失真、文字水印",
            "default_duration": 5,
            "is_preset": True,
            "sort_order": 5,
        },
        {
            "style_code": "animal_kingdom",
            "style_name": "动物乐园",
            "style_icon": "🐾",
            "description": "动物走路奔跑，摇头摆尾，互相嬉戏玩耍",
            "category": "animal",
            "system_prompt": "让画面中的动物活起来。动物们走路、奔跑、跳跃，互相嬉戏玩耍，摇头摆尾，发出可爱的动作和表情。保持画作原有的色彩和稚嫩笔触风格。",
            "negative_prompt": "恐怖、暴力、成人内容、画面变形、色彩失真、文字水印",
            "default_duration": 5,
            "is_preset": True,
            "sort_order": 6,
        },
        {
            "style_code": "four_seasons",
            "style_name": "四季变换",
            "style_icon": "🌸",
            "description": "春夏秋冬循环变化，春花绽放，秋叶飘落，冬雪纷飞",
            "category": "nature",
            "system_prompt": "让画面展现四季的变化之美。春天花开蜂舞，夏天绿树成荫，秋天落叶飘飘，冬天雪花纷飞。四季自然过渡，画面充满诗意。保持画作原有的色彩和稚嫩笔触风格。",
            "negative_prompt": "恐怖、暴力、成人内容、画面变形、色彩失真、文字水印",
            "default_duration": 8,
            "is_preset": True,
            "sort_order": 7,
        },
        {
            "style_code": "custom_pro",
            "style_name": "自定义 PRO",
            "style_icon": "🔮",
            "description": "自主编写提示词，完全掌控动画效果",
            "category": "custom",
            "system_prompt": "",
            "user_prompt_prefix": "自定义提示词模式，请根据输入的创意生成动画。",
            "negative_prompt": "恐怖、暴力、成人内容",
            "default_duration": 5,
            "is_preset": True,
            "is_paid": True,
            "required_plan": "flagship",
            "sort_order": 8,
        },
    ]

    db = SessionLocal()
    try:
        existing = db.query(PromptTemplate).count()
        if existing >= len(PROMPTS):
            return
        for p in PROMPTS:
            if db.query(PromptTemplate).filter(PromptTemplate.style_code == p["style_code"]).first():
                continue
            template = PromptTemplate(**p)
            db.add(template)
        db.commit()
        logger.info(f"   已初始化 {len(PROMPTS)} 条提示词模板")
    except Exception as e:
        db.rollback()
        logger.warning(f"   提示词种子数据初始化跳过: {e}")
    finally:
        db.close()


# ==================== 创建 App ====================

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.APP_DEBUG else None,
    redoc_url=None,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 路由
app.include_router(api_router, prefix=settings.API_PREFIX)

# 确保静态文件目录存在（必须在 mount 前创建）
os.makedirs("local_storage", exist_ok=True)
os.makedirs("frontend", exist_ok=True)

# 静态文件（Web 前端页面 & 本地存储）
app.mount("/local", StaticFiles(directory="local_storage"), name="local_storage")
app.mount("/app", StaticFiles(directory="frontend", html=True), name="frontend")


# ==================== 开发登录（仅 MVP 阶段使用） ====================

from fastapi import APIRouter, Depends
from pydantic import BaseModel as PydanticModel

dev_router = APIRouter()


class DevLoginRequest(PydanticModel):
    nickname: str = "测试用户"


@dev_router.post("/auth/dev-login", summary="[DEV] 开发环境登录")
def dev_login(req: DevLoginRequest):
    """
    ⚠️ 开发环境专用：直接创建/登录用户，跳过微信认证。
    生产环境请移除此接口。
    """
    db = SessionLocal()
    try:
        # 按昵称查找已有用户
        user = db.query(User).filter(User.nickname == req.nickname).first()
        if not user:
            user = User(
                wechat_openid=f"dev_{uuid.uuid4().hex[:12]}",
                nickname=req.nickname,
                role="individual",
                personal_quota=10,
                personal_plan="yearly",
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"创建开发用户: {req.nickname} (id={user.id})")

        token = create_access_token(data={"user_id": user.id, "openid": user.wechat_openid})
        from app.utils.response import success
        return success(data={
            "access_token": token,
            "token_type": "bearer",
            "user_id": user.id,
            "nickname": user.nickname,
            "role": user.role,
            "remaining_quota": user.personal_quota - user.personal_used,
        })
    finally:
        db.close()


app.include_router(dev_router, prefix=settings.API_PREFIX)


# ==================== 健康检查 ====================

@app.get("/health")
def health_check():
    return {"status": "ok", "app": settings.APP_NAME, "env": settings.APP_ENV}
