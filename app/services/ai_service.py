"""
AI 服务封装
- 调用阿里万象 (DashScope) 图生视频（HTTP API，不依赖SDK特定版本）
- 图片内容识别与风格推荐
- 任务轮询
"""
from __future__ import annotations
import re
import time
import requests
from loguru import logger

from app.core.config import settings


# DashScope API 基础地址
DASHSCOPE_API_BASE = "https://dashscope.aliyuncs.com/api/v1"

# 关键词 → 风格映射表（style_code 必须与数据库一致）
# 注意：必须覆盖足够宽泛的关键词，确保 AI 分析的各种描述都能匹配到
KEYWORD_STYLE_MAP = [
    # 海底世界
    (["海洋", "鱼", "海豚", "鲸鱼", "海底", "水母", "鲨鱼", "海龟", "珊瑚", "贝壳", "大海", "海浪", "沙滩", "船", "小岛", "游泳"], "ocean_world"),
    # 自然奥秘
    (["森林", "树", "鸟", "花", "草", "蝴蝶", "蜜蜂", "阳光", "叶子", "蘑菇", "小溪", "山水", "竹子", "梅花", "云雾", "江河", "国画", "中国风", "毛笔", "春天", "秋天", "冬天", "夏天", "季节", "花园", "公园", "草地", "蓝天", "白云", "风筝"], "nature_wonder"),
    # 太空冒险
    (["太空", "星球", "火箭", "宇宙", "外星人", "星星", "地球", "宇航员", "飞船", "银河", "机器人", "科技", "电脑", "齿轮", "机器", "未来", "机甲", "科幻"], "space_adventure"),
    # 魔法童话
    (["城堡", "公主", "王冠", "魔法", "王子", "国王", "皇后", "精灵", "仙女", "童话", "神话", "传说", "骑士", "龙", "独角兽", "梦幻", "奇迹"], "magic_fairytale"),
    # 动物乐园
    (["恐龙", "霸王龙", "化石", "火山", "翼龙", "远古", "动物", "小猫", "小狗", "兔子", "熊", "老虎", "狮子", "大象", "猴子", "熊猫", "长颈鹿", "斑马", "企鹅", "猫头鹰", "宠物"], "animal_kingdom"),
    # 节日欢庆
    (["彩虹", "云朵", "泡泡", "彩带", "糖果", "气球", "节日", "派对", "烟花", "生日", "蛋糕", "礼物", "彩色", "鲜艳", "明亮", "欢快", "活泼", "快乐", "开心", "热闹", "庆祝"], "festival_celebration"),
    # 四季变换
    (["四季", "春夏秋冬", "落叶", "雪花", "融化", "发芽", "丰收", "雪花"], "four_seasons"),
]


def _match_styles(description: str) -> list[str]:
    """根据描述文本匹配风格，匹配不足3个时用默认风格补齐"""
    scores = {}
    for keywords, style_code in KEYWORD_STYLE_MAP:
        score = sum(1 for kw in keywords if kw in description)
        if score > 0:
            scores[style_code] = score
    # 按匹配度排序
    sorted_styles = sorted(scores.keys(), key=lambda s: scores[s], reverse=True)
    # 不足3个时用默认通用风格补齐（去重）
    fallback = ["magic_fairytale", "nature_wonder", "festival_celebration"]
    for fb in fallback:
        if fb not in sorted_styles:
            sorted_styles.append(fb)
    return sorted_styles[:3]


# --------------------------------
#  动物检测 → 动画提示词音效增强
# --------------------------------
ANIMAL_SOUND_MAP = {
    # 常见宠物
    "猫": "一只喵喵叫的小猫在画面里快乐地走动，发出可爱的喵喵声",
    "小猫": "一只喵喵叫的小花猫在画面里蹦蹦跳跳，发出软萌的喵喵声",
    "狗": "一只汪汪叫的可爱小狗摇着尾巴跑动，汪汪地叫个不停",
    "小狗": "一只毛茸茸的小狗汪汪叫着，欢快地跑来跑去",
    # 农场动物
    "鸡": "一只咯咯叫的大公鸡昂首挺胸，发出清脆的咯咯声",
    "公鸡": "一只大公鸡咯咯地打鸣，声音响亮又精神",
    "母鸡": "一只母鸡咯咯哒地叫着，在院子里走来走去",
    "小鸡": "几只毛茸茸的小鸡叽叽喳喳地叫着，跟着母鸡跑来跑去",
    "鸭": "一只嘎嘎叫的小黄鸭摇摇摆摆地走路，嘎嘎嘎的声音很可爱",
    "鸭子": "一只小鸭子在水中游来游去，发出嘎嘎嘎的叫声",
    "小鸭": "几只毛茸茸的小黄鸭嘎嘎叫着，跟着鸭妈妈走",
    "牛": "一头哞哞叫的大奶牛慢慢走在草地上，发出低沉的哞哞声",
    "奶牛": "一头黑白花的奶牛哞哞叫着，悠闲地吃着草",
    "羊": "几只咩咩叫的小白羊蹦蹦跳跳，发出温柔的咩咩声",
    "小羊": "一只软绵绵的小绵羊咩咩叫着，在草地上吃草",
    "马": "一匹骏马嘶鸣着在草原上奔跑，鬃毛随风飘扬，发出响亮的嘶鸣声",
    "猪": "一头粉嫩的小猪哼哼唧唧地拱着地，发出可爱的哼哼声",
    "小猪": "一只圆滚滚的小粉猪哼哼叫着，快乐地打滚",
    # 野生动物
    "兔子": "一只蹦蹦跳跳的小白兔竖起长耳朵，在草地上轻快地跳跃",
    "小白兔": "一只雪白的小兔子竖起耳朵，蹦蹦跳跳地跑过来",
    "鸟": "几只彩色的小鸟在树枝上啾啾鸣叫，声音清脆悦耳",
    "小鸟": "可爱的小鸟站在枝头啾啾啾地唱歌，声音清脆动听",
    "大象": "一头灰色的大象甩着长鼻子，发出呜呜的叫声",
    "老虎": "一只威风的小老虎嗷呜地叫了一声，甩了甩尾巴",
    "狮子": "一只雄狮大声吼叫着，鬃毛随风抖动，充满王者威风",
    "猴子": "几只小猴子吱吱叫着，在树上荡来荡去，活泼极了",
    "熊猫": "一只可爱的熊猫宝宝嘤嘤叫着，抱着竹子啃个不停",
    "长颈鹿": "一只高高的长颈鹿低头吃着树叶，脖子优雅地弯曲",
    "企鹅": "几只胖胖的企鹅摇摇摆摆地走在冰面上，发出咕咕的叫声",
    "熊": "一头憨憨的小熊嗷嗷叫着，在森林里慢慢地散步",
    # 昆虫小动物
    "青蛙": "一只绿色的小青蛙呱呱叫着，在水边跳来跳去",
    "鱼": "五彩斑斓的小鱼在水中游来游去，吐着泡泡发出啵啵的声音",
    "小鱼": "几条漂亮的小鱼摆着尾巴，在水中自由自在地游动",
    "蜜蜂": "几只小蜜蜂嗡嗡嗡地飞来飞去，在花丛中采蜜",
    "蝴蝶": "几只彩色蝴蝶扑闪着翅膀在花间飞舞，翅膀闪闪发光",
    "毛毛虫": "一条绿色的毛毛虫一拱一拱地在叶子上爬行，不紧不慢",
    "蜗牛": "一只小蜗牛背着壳慢慢爬行，触角轻轻摇晃",
    "瓢虫": "一只红色的小瓢虫在绿叶上爬来爬去，翅膀轻轻张开又合拢",
    "蚂蚁": "几只小蚂蚁排着队来来往往，勤快地搬运着食物",
    # 恐龙
    "恐龙": "一只小恐龙嗷嗷地吼叫着，摇着尾巴在远古丛林中走动",
    "霸王龙": "一只小霸王龙张大嘴巴嗷地吼了一声，迈着大步走路",
    # 海洋动物
    "海豚": "一只海豚在海面上跃起，发出清脆悦耳的啾啾声",
    "鲸鱼": "一头大鲸鱼在深海中缓缓游动，发出低沉的呜鸣声",
    "水母": "几只透明的水母在水中优雅地飘动，散发着柔和的荧光",
    "鲨鱼": "一条小鲨鱼摆着尾巴在水中游动，露出锋利的牙齿",
    "海龟": "一只海龟慢悠悠地在海底爬行，时不时冒出几个小泡泡",
}


def _detect_animals(description: str) -> list[dict]:
    """
    从画作描述中检测动物，返回动物及对应声音描述。
    长关键词优先匹配，避免"小猫"被"猫"覆盖。
    """
    # 按关键词长度降序排列，长词优先匹配
    sorted_keys = sorted(ANIMAL_SOUND_MAP.keys(), key=lambda k: len(k), reverse=True)
    detected = []
    used = set()
    desc_consumed = description

    for keyword in sorted_keys:
        if keyword in desc_consumed:
            # 检查是否已被更长关键词覆盖
            base_key = keyword
            is_covered = False
            for longer_key in used:
                if base_key in longer_key:
                    is_covered = True
                    break
            if not is_covered:
                detected.append({
                    "animal": keyword,
                    "sound_desc": ANIMAL_SOUND_MAP[keyword],
                })
                used.add(keyword)

    return detected


class AIService:
    """阿里万象视频生成服务（使用 HTTP API）"""

    # 图生视频模型（首帧生视频）
    VIDEO_MODEL = "wan2.7-i2v-2026-04-25"

    @staticmethod
    def _get_image_data(image_url: str) -> str:
        """
        将图片转为 DashScope 可用的 HTTP URL。
        DashScope img_url 只接受 HTTP/HTTPS URL，不支持 base64 data URI。
        """
        if not image_url:
            return ""

        # 本地路径 /local/xxx.jpg → http://公网IP:8000/local/xxx.jpg
        if image_url.startswith("/local/"):
            return f"http://{settings.SELF_HOST}{image_url}"

        # 已是 http/https URL，直接返回
        if image_url.startswith("http://") or image_url.startswith("https://"):
            return image_url

        return image_url

    @staticmethod
    def generate_video(
        image_url: str,
        prompt: str,
        negative_prompt: str = "",
        duration: int = 5,
        resolution: str = "720p",
    ) -> str | None:
        """
        提交图生视频任务，返回 task_id（异步）
        
        使用 DashScope HTTP API，不依赖特定SDK版本
        """
        try:
            api_key = settings.DASHSCOPE_API_KEY
            if not api_key:
                logger.error("DASHSCOPE_API_KEY 未配置")
                return None

            # 处理图片（本地路径 → base64 或 HTTP URL）
            img_input = AIService._get_image_data(image_url)
            if not img_input:
                logger.error("图片路径为空")
                return None

            logger.info(
                f"提交视频生成任务 | img_len={len(img_input)} | prompt={prompt[:60]}..."
            )

            # 构造请求体
            payload = {
                "model": AIService.VIDEO_MODEL,
                "input": {
                    "prompt": prompt,
                    "img_url": img_input,
                },
                "parameters": {
                    "resolution": resolution.upper(),
                    "duration": duration,
                    "prompt_extend": True,
                    "watermark": False,
                },
            }

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "X-DashScope-Async": "enable",
            }

            resp = requests.post(
                f"{DASHSCOPE_API_BASE}/services/aigc/video-generation/video-synthesis",
                json=payload,
                headers=headers,
                timeout=settings.DASHSCOPE_TIMEOUT,
            )

            logger.info(f"API响应状态: {resp.status_code} | body前200字符: {resp.text[:200]}")

            if resp.status_code == 200:
                data = resp.json()
                task_id = data.get("output", {}).get("task_id")
                if task_id:
                    logger.info(f"任务提交成功，task_id={task_id}")
                    return task_id
                else:
                    logger.error(f"响应中无task_id: {data}")
                    return None
            else:
                logger.error(
                    f"任务提交失败: HTTP {resp.status_code} - {resp.text[:300]}"
                )
                return None

        except Exception as e:
            logger.error(f"generate_video 异常: {e}")
            return None

    @staticmethod
    def poll_task(task_id: str, max_wait: int = 180) -> dict | None:
        """
        轮询任务结果，直到完成或超时
        返回 {"video_url": "..."} 或 {"error": "..."}
        
        使用 DashScope HTTP API
        """
        try:
            api_key = settings.DASHSCOPE_API_KEY
            if not api_key:
                return {"error": "DASHSCOPE_API_KEY 未配置"}

            start = time.time()
            check_interval = 10

            headers = {
                "Authorization": f"Bearer {api_key}",
            }

            while True:
                elapsed = time.time() - start
                if elapsed > max_wait:
                    logger.warning(f"任务轮询超时，task_id={task_id}")
                    return {"error": "轮询超时"}

                resp = requests.get(
                    f"{DASHSCOPE_API_BASE}/tasks/{task_id}",
                    headers=headers,
                    timeout=30,
                )

                if resp.status_code != 200:
                    logger.warning(
                        f"查询任务失败: HTTP {resp.status_code} - {resp.text[:200]}"
                    )
                    time.sleep(check_interval)
                    continue

                data = resp.json()
                output = data.get("output", {})
                status = output.get("task_status", "UNKNOWN")
                logger.info(f"任务状态: {status} | 已等待 {int(elapsed)}s")

                if status == "SUCCEEDED":
                    video_url = output.get("video_url")
                    if video_url:
                        logger.info(f"任务完成，video_url={video_url[:80]}...")
                        return {"video_url": video_url}
                    else:
                        # 尝试从 results 取
                        results = output.get("results", [])
                        if results and len(results) > 0:
                            url = results[0].get("url", "")
                            return {"video_url": url}
                        return {"error": "任务完成但未返回视频地址"}

                elif status in ("FAILED", "UNKNOWN"):
                    msg = output.get("message", "任务失败")
                    logger.error(f"任务失败: {msg}")
                    return {"error": msg}

                # 继续等待
                time.sleep(check_interval)

        except Exception as e:
            logger.error(f"poll_task 异常: {e}")
            return {"error": str(e)}

    @staticmethod
    def analyze_image(image_url: str) -> dict | None:
        """
        分析画作内容，返回描述 + 推荐风格
        返回 {"description": "...", "recommended_styles": ["ocean", "forest", ...]}
        """
        try:
            from dashscope import MultiModalConversation

            img_url = AIService._get_image_data(image_url)
            if not img_url:
                return None

            messages = [
                {
                    "role": "system",
                    "content": [{"text": "你是一个幼儿画作分析助手。用一段简短中文描述这幅画的内容（主题、颜色、场景）。"}],
                },
                {
                    "role": "user",
                    "content": [
                        {"image": img_url},
                        {"text": "请分析这幅幼儿画作的内容，描述它画了什么，采用了什么颜色，表现了什么主题"},
                    ],
                },
            ]

            logger.info("正在分析画作内容...")
            response = MultiModalConversation.call(
                model="qwen-vl-plus",
                messages=messages,
                api_key=settings.DASHSCOPE_API_KEY,
            )

            if response.status_code == 200:
                description = response.output.choices[0].message.content[0].get("text", "")
                if isinstance(description, list):
                    description = " ".join(description) if isinstance(description[0], str) else str(description)
                description = str(description).strip()
                logger.info(f"画作描述: {description[:100]}")

                recommended = _match_styles(description)
                animals = _detect_animals(description)
                logger.info(f"检测到动物: {[a['animal'] for a in animals]}")
                return {
                    "description": description,
                    "recommended_styles": recommended,
                    "detected_animals": animals,
                }
            else:
                logger.error(f"画作分析失败: {response.status_code} - {response.message}")
                return None

        except Exception as e:
            logger.error(f"analyze_image 异常: {e}")
            return None

    @staticmethod
    def generate_image(prompt: str, size: str = "1024*1024") -> str | None:
        """
        文生图（备用）
        """
        try:
            from dashscope import ImageSynthesis

            response = ImageSynthesis.call(
                model="wanx-v1",
                prompt=prompt,
                size=size,
                api_key=settings.DASHSCOPE_API_KEY,
            )

            if response.status_code == 200:
                results = response.output.results
                if results and len(results) > 0:
                    return results[0]["url"]
                return None
            else:
                logger.error(
                    f"文生图失败: {response.status_code} - {response.message}"
                )
                return None

        except Exception as e:
            logger.error(f"generate_image 异常: {e}")
            return None
