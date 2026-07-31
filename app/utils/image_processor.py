"""
图像预处理工具
- 透视校正
- 自动裁剪
- 色彩增强
- 尺寸归一化
"""
from __future__ import annotations
import io
import base64
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np


class ImageProcessor:
    """画作图像预处理"""

    TARGET_SIZE = (1024, 1024)  # 阿里万象推荐输入尺寸
    MAX_SIZE = (2048, 2048)

    @staticmethod
    def enhance(image: Image.Image) -> Image.Image:
        """画作色彩增强 - 让幼儿画作更鲜艳"""
        # 适度增加对比度
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.15)

        # 适度增加饱和度
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(1.1)

        # 轻微锐化
        image = image.filter(ImageFilter.SHARPEN)

        return image

    @staticmethod
    def auto_crop(image: Image.Image, padding: int = 20) -> Image.Image:
        """
        自动裁剪：检测画作边缘并裁剪到画作区域
        """
        img_array = np.array(image.convert("RGB"))
        gray = np.mean(img_array, axis=2)

        # 检测非白色/非背景区域
        bg_threshold = 240
        non_bg = gray < bg_threshold

        if not non_bg.any():
            return image

        rows = np.any(non_bg, axis=1)
        cols = np.any(non_bg, axis=0)
        y_min, y_max = np.where(rows)[0][[0, -1]]
        x_min, x_max = np.where(cols)[0][[0, -1]]

        # 添加 padding
        h, w = img_array.shape[:2]
        y_min = max(0, y_min - padding)
        y_max = min(h, y_max + padding)
        x_min = max(0, x_min - padding)
        x_max = min(w, x_max + padding)

        return image.crop((x_min, y_min, x_max, y_max))

    @staticmethod
    def resize_to_target(image: Image.Image) -> Image.Image:
        """按比例缩放到目标尺寸，保持长宽比"""
        image.thumbnail(ImageProcessor.TARGET_SIZE, Image.Resampling.LANCZOS)
        return image

    @staticmethod
    def process_full_pipeline(image_data: bytes) -> tuple[Image.Image, bytes]:
        """
        完整预处理流水线
        返回: (处理后的PIL图片, 处理后的字节数据)
        """
        image = Image.open(io.BytesIO(image_data))

        # 转换 RGBA → RGB（如果有透明通道）
        if image.mode == "RGBA":
            background = Image.new("RGB", image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[3])
            image = background
        elif image.mode != "RGB":
            image = image.convert("RGB")

        # 1. 自动裁剪
        image = ImageProcessor.auto_crop(image)

        # 2. 色彩增强
        image = ImageProcessor.enhance(image)

        # 3. 尺寸归一化
        image = ImageProcessor.resize_to_target(image)

        # 4. 输出
        output = io.BytesIO()
        image.save(output, format="JPEG", quality=95)
        output.seek(0)

        return image, output.read()
