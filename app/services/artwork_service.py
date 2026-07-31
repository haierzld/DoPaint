"""
画作服务
- 上传、预处理、存储（OSS / 本地降级）
- 同租户图片去重（SHA256 哈希）
"""
from __future__ import annotations
import hashlib
import os
import uuid
from io import BytesIO
from PIL import Image
from sqlalchemy.orm import Session
from loguru import logger

from app.core.config import settings
from app.models.artwork import Artwork


class ArtworkService:
    """画作管理"""

    UPLOAD_DIR_ORIGINAL = "artworks/original/"
    UPLOAD_DIR_PROCESSED = "artworks/processed/"
    UPLOAD_DIR_THUMB = "artworks/thumb/"

    def __init__(self, db: Session):
        self.db = db
        self._oss_available = bool(
            settings.OSS_ACCESS_KEY_ID and settings.OSS_ACCESS_KEY_SECRET
        )

    def upload_and_process(
        self,
        user_id: int,
        org_id: int | None,
        image_data: bytes,
        title: str = "",
        author_name: str = "",
        source: str = "camera",
    ) -> Artwork:
        """
        上传画作 → 同租户去重 → 预处理 → 存储 → 写入数据库
        如果同租户下已存在相同图片（SHA256 匹配），直接返回已有画作
        """
        # 0. 计算图片哈希，同租户去重检查
        image_hash = hashlib.sha256(image_data).hexdigest()

        if org_id is not None:
            existing = (
                self.db.query(Artwork)
                .filter(
                    Artwork.org_id == org_id,
                    Artwork.image_hash == image_hash,
                )
                .first()
            )
        else:
            # 无机构时按用户去重
            existing = (
                self.db.query(Artwork)
                .filter(
                    Artwork.user_id == user_id,
                    Artwork.org_id.is_(None),
                    Artwork.image_hash == image_hash,
                )
                .first()
            )

        if existing:
            logger.info(f"发现重复图片，hash={image_hash[:16]}...，返回已有画作 id={existing.id}")
            existing.is_duplicate = True
            return existing

        file_id = uuid.uuid4().hex[:12]
        ext = "jpg"

        # 1. 上传原始图片
        original_key = f"{self.UPLOAD_DIR_ORIGINAL}{file_id}_original.{ext}"
        original_url = self._store(original_key, image_data)

        # 2. 图像预处理 + 处理图存储
        try:
            from app.utils.image_processor import ImageProcessor
            processed_img, processed_data = ImageProcessor.process_full_pipeline(image_data)
            processed_key = f"{self.UPLOAD_DIR_PROCESSED}{file_id}_processed.{ext}"
            processed_url = self._store(processed_key, processed_data)
        except Exception as e:
            logger.warning(f"图像预处理失败，使用原图: {e}")
            processed_url = original_url

        # 3. 生成缩略图
        thumb_key = f"{self.UPLOAD_DIR_THUMB}{file_id}_thumb.{ext}"
        try:
            thumb_img = Image.open(BytesIO(image_data))
            thumb_img.thumbnail((300, 300))
            thumb_buf = BytesIO()
            thumb_img.save(thumb_buf, format="JPEG", quality=80)
            thumb_url = self._store(thumb_key, thumb_buf.getvalue())
        except Exception:
            thumb_url = original_url

        # 4. 写入数据库
        artwork = Artwork(
            user_id=user_id,
            org_id=org_id,
            title=title or f"画作_{file_id}",
            author_name=author_name,
            original_url=original_url,
            processed_url=processed_url,
            thumbnail_url=thumb_url,
            image_hash=image_hash,
            source=source,
            status="completed",
        )
        self.db.add(artwork)
        self.db.commit()
        self.db.refresh(artwork)

        artwork.is_duplicate = False
        return artwork

    def _store(self, key: str, data: bytes) -> str:
        """存储文件，优先 OSS -> 降级本地"""
        if self._oss_available:
            try:
                return self._upload_oss(key, data)
            except Exception as e:
                logger.warning(f"OSS上传失败，降级本地: {e}")

        return self._save_local(key, data)

    def _upload_oss(self, key: str, data: bytes) -> str:
        """上传到阿里云 OSS，返回完整 URL"""
        import oss2
        auth = oss2.Auth(settings.OSS_ACCESS_KEY_ID, settings.OSS_ACCESS_KEY_SECRET)
        bucket = oss2.Bucket(auth, settings.OSS_ENDPOINT, settings.OSS_BUCKET_NAME)
        bucket.put_object(key, data)

        if settings.OSS_CDN_DOMAIN:
            return f"{settings.OSS_CDN_DOMAIN}/{key}"
        return f"https://{settings.OSS_BUCKET_NAME}.{settings.OSS_ENDPOINT}/{key}"

    def _save_local(self, key: str, data: bytes) -> str:
        """保存到本地文件系统"""
        local_path = os.path.join("local_storage", key)
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        with open(local_path, "wb") as f:
            f.write(data)
        return f"/local/{key}"

    def get_list(
        self,
        org_id: int,
        page: int = 1,
        page_size: int = 20,
        status: str | None = None,
        keyword: str | None = None,
    ):
        """分页查询画作列表"""
        from app.models.animation import Animation

        query = self.db.query(Artwork).filter(Artwork.org_id == org_id)

        if status:
            query = query.filter(Artwork.status == status)
        if keyword:
            query = query.filter(
                Artwork.title.contains(keyword) | Artwork.author_name.contains(keyword)
            )

        total = query.count()
        artworks = (
            query.order_by(Artwork.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        result = []
        for aw in artworks:
            animation_count = (
                self.db.query(Animation)
                .filter(Animation.artwork_id == aw.id)
                .count()
            )
            result.append({
                "id": aw.id,
                "title": aw.title,
                "author_name": aw.author_name,
                "thumbnail_url": aw.thumbnail_url,
                "original_url": aw.original_url,
                "source": aw.source,
                "status": aw.status,
                "created_at": aw.created_at.isoformat() if aw.created_at else "",
                "animation_count": animation_count,
            })

        return result, total
