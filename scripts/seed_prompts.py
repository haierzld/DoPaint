"""
初始化提示词模板数据
运行: python -m scripts.seed_prompts
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.models.base import SessionLocal, engine, Base
from app.models.prompt_template import PromptTemplate


PROMPTS = [
    {
        "style_code": "magic_fairytale",
        "style_name": "魔法童话",
        "style_icon": "🧚",
        "description": "画面变成温馨童话世界，角色轻轻摆动微笑，星星和闪光飘落",
        "category": "story",
        "system_prompt": (
            "让画面变成一个温馨的魔法童话世界。"
            "画面中的角色轻轻摆动、微笑眨眼，"
            "周围有闪烁的星星和光点缓缓飘落，"
            "整体色调温暖柔和，带有梦幻光晕。"
            "保持画作原有的色彩和稚嫩笔触风格。"
        ),
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
        "system_prompt": (
            "让画面呈现大自然的生机与美好。"
            "花朵缓缓绽放，小草轻轻摇摆，"
            "蝴蝶翩翩飞舞，小鸟展翅飞翔，"
            "阳光透过树叶洒下温暖光斑。"
            "保持画作原有的色彩和稚嫩笔触风格。"
        ),
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
        "system_prompt": (
            "让画面充满节日喜庆氛围。"
            "角色欢快舞动，彩色气球升空飘荡，"
            "彩带飞舞，礼花绽放，"
            "温暖灯光闪烁，笑脸洋溢。"
            "保持画作原有的色彩和稚嫩笔触风格。"
        ),
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
        "system_prompt": (
            "让画面变成神秘美丽的海底世界。"
            "彩色的鱼儿自由游动，珊瑚轻轻摇摆，"
            "一串串气泡缓缓上升，"
            "阳光透过水面洒下蓝色光影。"
            "保持画作原有的色彩和稚嫩笔触风格。"
        ),
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
        "system_prompt": (
            "让画面变成浩瀚神奇的太空。"
            "星星闪烁发光，行星缓缓运转，"
            "画面中的角色漂浮在星空中，"
            "远处有璀璨的银河。"
            "保持画作原有的色彩和稚嫩笔触风格。"
        ),
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
        "system_prompt": (
            "让画面中的动物活起来。"
            "动物们走路、奔跑、跳跃，"
            "互相嬉戏玩耍，摇头摆尾，"
            "发出可爱的动作和表情。"
            "保持画作原有的色彩和稚嫩笔触风格。"
        ),
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
        "system_prompt": (
            "让画面展现四季的变化之美。"
            "春天花开蜂舞，夏天绿树成荫，"
            "秋天落叶飘飘，冬天雪花纷飞。"
            "四季自然过渡，画面充满诗意。"
            "保持画作原有的色彩和稚嫩笔触风格。"
        ),
        "negative_prompt": "恐怖、暴力、成人内容、画面变形、色彩失真、文字水印",
        "default_duration": 8,
        "is_preset": True,
        "sort_order": 7,
    },
    {
        "style_code": "custom_pro",
        "style_name": "自定义 PRO",
        "style_icon": "🔮",
        "description": "老师自主编写提示词，完全掌控动画效果",
        "category": "custom",
        "system_prompt": "",
        "user_prompt_prefix": "自定义提示词模式，请根据老师输入的创意生成动画。",
        "negative_prompt": "恐怖、暴力、成人内容",
        "default_duration": 5,
        "is_preset": True,
        "is_paid": True,
        "required_plan": "flagship",
        "sort_order": 8,
    },
]


def seed():
    """写入提示词数据"""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        existing = db.query(PromptTemplate).count()
        if existing > 0:
            print(f"已有 {existing} 条提示词数据，跳过初始化")
            return

        for p in PROMPTS:
            template = PromptTemplate(**p)
            db.add(template)

        db.commit()
        print(f"成功初始化 {len(PROMPTS)} 条提示词模板")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
