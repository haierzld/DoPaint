"""
提示词模板模型
"""
from sqlalchemy import Column, String, Integer, Text, Float, Boolean
from app.models.base import BaseModel


class PromptTemplate(BaseModel):
    """提示词模板"""

    __tablename__ = "prompt_templates"

    style_code = Column(String(50), unique=True, nullable=False, comment="风格编号")
    style_name = Column(String(100), nullable=False, comment="风格名称")
    style_icon = Column(String(10), comment="风格图标emoji")
    description = Column(Text, comment="风格描述文案")
    category = Column(String(50), comment="分类：story/nature/festival/ocean/space/animal/custom")

    # 提示词
    system_prompt = Column(Text, nullable=False, comment="系统提示词模板")
    user_prompt_prefix = Column(Text, comment="用户提示词前缀")
    negative_prompt = Column(Text, comment="负向提示词")

    # 参数
    default_duration = Column(Integer, default=5, comment="默认时长(秒)")
    default_resolution = Column(String(20), default="720p", comment="默认分辨率")

    # 展示
    thumbnail = Column(String(500), comment="示例缩略图URL")
    demo_video_url = Column(String(500), comment="示例视频URL")

    # 权限
    is_preset = Column(Boolean, default=True, comment="是否系统预设")
    is_paid = Column(Boolean, default=False, comment="是否付费模板")
    price = Column(Float, default=0, comment="单独购买价格")
    required_plan = Column(String(50), comment="最低套餐要求")

    # 排序
    sort_order = Column(Integer, default=0)
    status = Column(Integer, default=1, comment="1-启用 0-禁用")
