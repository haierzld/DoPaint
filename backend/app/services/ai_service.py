"""
AI 服务封装
- 调用阿里万象 (DashScope) 图生视频（HTTP API，不依赖SDK特定版本）
- 图片内容识别与风格推荐
- 任务轮询
"""
from __future__ import annotations
import os
import base64
import re
import time
import requests
from loguru import logger

from app.core.config import settings


# DashScope API 基础地址
DASHSCOPE_API_BASE = "https://dashscope.aliyuncs.com/api/v1"

# 关键词 → 风格映射表（style_code 必须与数据库一致）
KEYWORD_STYLE_MAP = [
    (["海洋", "鱼", "海豚", "鲸鱼", "海底", "水母", "鲨鱼", "海龟", "珊瑚", "贝壳"], "ocean_world"),
    (["森林", "树", "鸟", "花", "草", "蝴蝶", "蜜蜂", "阳光", "叶子", "蘑菇", "小溪"], "nature_wonder"),
    (["太空", "星球", "火箭", "宇宙", "外星人", "星星", "地球", "宇航员", "飞船", "银河"], "space_adventure"),
    (["城堡", "公主", "王冠", "魔法", "王子", "国王", "皇后", "精灵", "仙女", "童话"], "magic_fairytale"),
    (["恐龙", "霸王龙", "化石", "火山", "翼龙", "远古", "动物", "小猫", "小狗", "兔子", "熊", "老虎", "狮子", "大象"], "animal_kingdom"),
    (["彩虹", "云朵", "泡泡", "彩带", "糖果", "气球", "节日", "派对", "烟花", "生日"], "festival_celebration"),
    (["水墨", "山水", "竹子", "梅花", "云雾", "江河", "国画", "中国风", "毛笔"], "nature_wonder"),
    (["机器人", "机甲", "科技", "电脑", "齿轮", "机器", "未来"], "space_adventure"),
]


def _match_styles(description: str) -> list[str]:
    """根据描述文本匹配风格"""
    scores = {}
    for keywords, style_code in KEYWORD_STYLE_MAP:
        score = sum(1 for kw in keywords if kw in description)
        if score > 0:
            scores[style_code] = score
    # 按匹配度排序，返回前3个
    sorted_styles = sorted(scores.keys(), key=lambda s: scores[s], reverse=True)
    return sorted_styles[:3]


class AIService:
    """阿里万象视频生成服务（使用 HTTP API）"""

    # 图生视频模型（首帧生视频）
    VIDEO_MODEL = "wan2.6-i2v-flash"

    @staticmethod
    def _get_image_data(image_url: str) -> str:
        """
        将图片转为 DashScope 可用的格式。
        本地路径 → 读取文件 → data:image/jpeg;base64,xxx
        """
        if not image_url:
            return ""

        # 本地路径 /local/xxx.jpg → 读取本地文件
        if image_url.startswith("/local/"):
            local_path = os.path.join("local_storage", image_url.replace("/local/", ""))
            if os.path.exists(local_path):
                with open(local_path, "rb") as f:
                    data = f.read()
                b64 = base64.b64encode(data).decode("utf-8")
                return f"data:image/jpeg;base64,{b64}"
            else:
                logger.warning(f"本地图片不存在: {local_path}")
                return image_url

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
                timeout=60,
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
            import dashscope
            from dashscope import MultiModalConversation

            img_b64 = AIService._get_image_data(image_url)
            if not img_b64:
                return None

            # 如果已经是 base64 data uri，提取纯 base64
            if "base64," in img_b64:
                img_b64 = img_b64.split("base64,", 1)[1]

            messages = [
                {
                    "role": "system",
                    "content": [{"text": "你是一个幼儿画作分析助手。用一段简短中文描述这幅画的内容（主题、颜色、场景）。"}],
                },
                {
                    "role": "user",
                    "content": [
                        {"image": f"data:image/jpeg;base64,{img_b64}"},
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
                return {
                    "description": description,
                    "recommended_styles": recommended,
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
