"""
画作模型
"""
from sqlalchemy import Column, String, Integer, BigInteger, Enum as SqlEnum, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Artwork(BaseModel):
    """幼儿画作"""

    __tablename__ = "artworks"

    user_id = Column(BigInteger, nullable=False, index=True, comment="上传者ID")
    org_id = Column(BigInteger, index=True, comment="所属机构ID")

    # 画作信息
    title = Column(String(200), comment='画作名称（可为空，如"小明的太阳"）')
    author_name = Column(String(50), comment="作者（幼儿名字）")

    # 图片
    original_url = Column(String(500), nullable=False, comment="原始图片URL")
    processed_url = Column(String(500), comment="预处理后图片URL")
    thumbnail_url = Column(String(500), comment="缩略图URL")

    # 来源
    source = Column(
        SqlEnum("camera", "album"),
        default="camera",
        comment="来源：camera-拍摄 album-相册",
    )

    # 状态
    status = Column(
        SqlEnum("pending", "processing", "completed", "failed"),
        default="pending",
        comment="处理状态",
    )
    process_error = Column(Text, comment="处理失败原因")

    # 关系
    animations = relationship("Animation", back_populates="artwork", lazy="dynamic", cascade="all, delete-orphan")
