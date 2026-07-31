"""
动画生成记录模型
"""
from sqlalchemy import Column, String, Integer, BigInteger, Float, Enum as SqlEnum, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Animation(BaseModel):
    """动画生成记录"""

    __tablename__ = "animations"

    artwork_id = Column(BigInteger, ForeignKey("artworks.id"), nullable=False, index=True, comment="画作ID")
    artwork = relationship("Artwork", back_populates="animations", foreign_keys=[artwork_id])
    user_id = Column(BigInteger, nullable=False, index=True, comment="创建者ID")
    org_id = Column(BigInteger, index=True, comment="所属机构ID")

    # 提示词
    prompt_style = Column(String(50), nullable=False, comment="风格编号")
    custom_prompt = Column(Text, comment="自定义提示词")
    final_prompt = Column(Text, comment="最终完整提示词")
    negative_prompt = Column(Text, comment="负向提示词")

    # AI 任务
    ai_task_id = Column(String(100), comment="阿里万象任务ID")
    ai_model = Column(String(100), comment="使用的模型")

    # 结果
    video_url = Column(String(500), comment="生成视频URL")
    thumbnail_url = Column(String(500), comment="视频缩略图URL")
    duration = Column(Integer, default=5, comment="视频时长(秒)")
    resolution = Column(String(20), default="720p", comment="分辨率")

    # 成本
    api_cost = Column(Float, default=0, comment="API调用成本(元)")

    # 状态
    status = Column(
        SqlEnum("queued", "generating", "completed", "failed"),
        default="queued",
        comment="生成状态",
    )
    error_msg = Column(Text, comment="失败原因")
    retry_count = Column(Integer, default=0, comment="重试次数")
    completed_at = Column(DateTime, comment="完成时间")
