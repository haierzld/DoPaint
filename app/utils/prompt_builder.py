"""
提示词组装器
根据画作特征和用户选择的风格，生成最终的 AI 提示词
"""
from typing import Optional
from app.models.prompt_template import PromptTemplate


class PromptBuilder:
    """提示词组装"""

    # 各风格预设的系统级描述
    STYLE_PREFIXES = {
        "magic_fairytale": "温暖的魔法童话世界风格。",
        "nature_wonder": "生机勃勃的自然奥秘风格。",
        "festival_celebration": "热闹欢快的节日庆典风格。",
        "ocean_world": "神秘美丽的海底世界风格。",
        "space_adventure": "浩瀚神奇的太空冒险风格。",
        "animal_kingdom": "活泼可爱的动物乐园风格。",
        "four_seasons": "春夏秋冬四季变换风格。",
    }

    # 全局通用前缀
    GLOBAL_PREFIX = (
        "这是一幅幼儿园小朋友的画作。"
        "请将这幅静态画作转化为流畅自然的5秒短视频动画。"
        "画面中的角色和物体会轻轻移动、摇摆或微笑，"
        "保持画作的原有色彩和稚嫩笔触风格，"
        "不要改变画作的构图和内容。"
        "画面温馨友爱，适合幼儿观看和教学展示。"
    )

    GLOBAL_NEGATIVE = (
        "恐怖、暴力、血腥、成人内容、"
        "画面变形扭曲、色彩严重失真、"
        "人物面容诡异、文字水印、"
        "画风剧烈改变、失去原有笔触"
    )

    @classmethod
    def build(
        cls,
        template: PromptTemplate,
        custom_prompt: Optional[str] = None,
        duration: int = 5,
        resolution: str = "720p",
    ) -> dict:
        """
        组装完整提示词
        返回: { prompt, negative_prompt, duration, resolution }
        """
        if custom_prompt:
            # custom_prompt 已包含画作分析描述 + 风格指令，GLOBAL_PREFIX 作为系统约束
            final_prompt = f"{cls.GLOBAL_PREFIX}\n{custom_prompt}"
            negative_prompt = template.negative_prompt or cls.GLOBAL_NEGATIVE
        else:
            style_prefix = cls.STYLE_PREFIXES.get(template.style_code, "")
            final_prompt = f"{cls.GLOBAL_PREFIX}\n{style_prefix}\n{template.system_prompt}"

            if template.user_prompt_prefix:
                final_prompt = f"{final_prompt}\n{template.user_prompt_prefix}"

            negative_prompt = template.negative_prompt or cls.GLOBAL_NEGATIVE

        return {
            "prompt": final_prompt.strip(),
            "negative_prompt": negative_prompt.strip(),
            "duration": duration or template.default_duration,
            "resolution": resolution or template.default_resolution,
        }
