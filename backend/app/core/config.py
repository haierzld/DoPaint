"""
应用配置管理
使用 pydantic-settings 读取 .env 文件
"""
from __future__ import annotations
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用全局配置"""

    # ---- 应用 ----
    APP_NAME: str = "DoPaint"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    APP_SECRET_KEY: str = "change-me"
    API_PREFIX: str = "/api/v1"
    SELF_HOST: str = "localhost:8000"  # 本服务公网地址，用于构造图片URL

    # ---- 数据库 ----
    DATABASE_URL: str = "mysql+pymysql://root:password@127.0.0.1:3306/dopaint"

    # ---- Redis ----
    REDIS_URL: str = "redis://127.0.0.1:6379/0"

    # ---- JWT ----
    JWT_SECRET_KEY: str = "jwt-secret-change-me"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200

    # ---- 微信小程序 ----
    WECHAT_APP_ID: str = ""
    WECHAT_APP_SECRET: str = ""

    # ---- 微信支付 ----
    WECHAT_PAY_MCH_ID: str = ""
    WECHAT_PAY_API_V3_KEY: str = ""
    WECHAT_PAY_SERIAL_NO: str = ""
    WECHAT_PAY_PRIVATE_KEY_PATH: str = ""
    WECHAT_PAY_NOTIFY_URL: str = ""

    # ---- 阿里云 OSS ----
    OSS_ACCESS_KEY_ID: str = ""
    OSS_ACCESS_KEY_SECRET: str = ""
    OSS_ENDPOINT: str = "oss-cn-hangzhou.aliyuncs.com"
    OSS_BUCKET_NAME: str = "dopaint-dev"
    OSS_CDN_DOMAIN: str = ""

    # ---- 阿里万象 (DashScope) ----
    DASHSCOPE_API_KEY: str = ""
    DASHSCOPE_VIDEO_MODEL: str = "wanx-v1-image-to-video"
    DASHSCOPE_MAX_RETRY: int = 3
    DASHSCOPE_TIMEOUT: int = 120

    # ---- 阿里云视觉智能 ----
    VISION_ACCESS_KEY_ID: str = ""
    VISION_ACCESS_KEY_SECRET: str = ""

    # ---- 配额 ----
    DEFAULT_FREE_QUOTA: int = 5
    DEFAULT_TRIAL_QUOTA: int = 500

    # ---- 上传限制 ----
    MAX_UPLOAD_SIZE_MB: int = 20
    ALLOWED_IMAGE_TYPES: str = "jpg,jpeg,png,webp,bmp"

    @property
    def allowed_image_extensions(self) -> list[str]:
        return [ext.strip() for ext in self.ALLOWED_IMAGE_TYPES.split(",")]

    @property
    def max_upload_bytes(self) -> int:
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

# ================================
# 将关键配置注入到 os.environ，确保三方 SDK 能读取
# ================================
_export_env_vars = {
    "DASHSCOPE_API_KEY": settings.DASHSCOPE_API_KEY,
}
for _key, _val in _export_env_vars.items():
    if _val:
        os.environ[_key] = _val
