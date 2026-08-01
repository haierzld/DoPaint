"""
画作接口
POST   /api/v1/artworks/upload        - 上传画作
GET    /api/v1/artworks                - 画作列表
GET    /api/v1/artworks/{id}           - 画作详情
DELETE /api/v1/artworks/{id}           - 删除画作
POST   /api/v1/artworks/batch-delete   - 批量删除
"""
from __future__ import annotations
from fastapi import APIRouter, Depends, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from loguru import logger

from app.core.deps import get_db, get_current_user
from app.core.config import settings
from app.services.artwork_service import ArtworkService
from app.services.ai_service import AIService
from app.models.user import User
from app.models.artwork import Artwork
from app.models.prompt_template import PromptTemplate
from app.utils.response import success, paginated, error

router = APIRouter()


@router.post("/upload", summary="上传画作")
async def upload_artwork(
    file: UploadFile = File(..., description="画作图片"),
    title: str = Form("", description="画作名称"),
    author_name: str = Form("", description="作者（幼儿名）"),
    source: str = Form("camera", description="来源 camera/album"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    上传幼儿画作 → 自动预处理 → 存储

    - 支持格式: jpg, jpeg, png, webp, bmp
    - 最大文件: 20MB
    - 自动裁剪、增强、归一化
    """
    # 校验文件类型
    ext = file.filename.rsplit(".", 1)[-1].lower() if file.filename and "." in file.filename else ""
    if ext not in settings.allowed_image_extensions:
        return error(f"不支持的文件格式，仅支持: {settings.ALLOWED_IMAGE_TYPES}")

    # 读取文件
    image_data = await file.read()

    # 高清图 VIP 校验：≥MAX_FREE_UPLOAD_MB 仅 VIP 用户可上传
    free_limit = settings.MAX_FREE_UPLOAD_MB * 1024 * 1024

    is_high_res = len(image_data) >= free_limit
    if is_high_res and current_user.personal_plan == "free":
        return error(
            f"高清图上传需开通 VIP 会员。当前图片 {len(image_data)/1024/1024:.1f}MB，"
            f"免费用户最大支持 {settings.MAX_FREE_UPLOAD_MB}MB。"
            f"开通 VIP 即可上传 {settings.MAX_UPLOAD_SIZE_MB}MB 高清画作并获得更高质量动画。",
            code=402
        )

    # 校验文件大小
    if len(image_data) > settings.max_upload_bytes:
        return error(f"文件过大，最大支持 {settings.MAX_UPLOAD_SIZE_MB}MB")

    # 处理
    svc = ArtworkService(db)
    artwork, compress_meta = svc.upload_and_process(
        user_id=current_user.id,
        org_id=current_user.org_id,
        image_data=image_data,
        title=title,
        author_name=author_name,
        source=source,
    )

    is_duplicate = getattr(artwork, "is_duplicate", False)

    # 图片压缩提示
    compress_msg = ""
    if compress_meta.get("was_compressed"):
        compress_msg = (
            f"图片已自动压缩: {compress_meta['original_size']/1024/1024:.1f}MB → "
            f"{compress_meta['final_size']/1024/1024:.1f}MB (节省 {compress_meta['compression_ratio']}%)"
        )

    return success(
        data={
            "id": artwork.id,
            "title": artwork.title,
            "author_name": artwork.author_name,
            "original_url": artwork.original_url,
            "processed_url": artwork.processed_url,
            "thumbnail_url": artwork.thumbnail_url,
            "source": artwork.source,
            "status": artwork.status,
            "created_at": artwork.created_at.isoformat() if artwork.created_at else "",
            "is_duplicate": is_duplicate,
            "is_high_res": is_high_res,
            "compress_msg": compress_msg,
        }
    )


@router.get("", summary="画作列表")
async def list_artworks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str = Query(None),
    keyword: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """分页查询画作列表"""
    org_id = current_user.org_id
    if not org_id:
        # 个人用户
        artworks = (
            db.query(Artwork)
            .filter(Artwork.user_id == current_user.id)
            .order_by(Artwork.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        total = (
            db.query(Artwork).filter(Artwork.user_id == current_user.id).count()
        )
        items = [
            {
                "id": a.id,
                "title": a.title,
                "author_name": a.author_name,
                "thumbnail_url": a.thumbnail_url,
                "original_url": a.original_url,
                "source": a.source,
                "status": a.status,
                "created_at": a.created_at.isoformat() if a.created_at else "",
                "animation_count": 0,
            }
            for a in artworks
        ]
    else:
        svc = ArtworkService(db)
        items, total = svc.get_list(
            org_id=org_id,
            page=page,
            page_size=page_size,
            status=status,
            keyword=keyword,
        )

    return paginated(items=items, total=total, page=page, page_size=page_size)


@router.get("/{artwork_id}", summary="画作详情")
async def get_artwork(
    artwork_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取画作详情"""
    artwork = db.query(Artwork).filter(Artwork.id == artwork_id).first()
    if not artwork:
        return error("画作不存在", code=404)

    return success(
        data={
            "id": artwork.id,
            "title": artwork.title,
            "author_name": artwork.author_name,
            "original_url": artwork.original_url,
            "processed_url": artwork.processed_url,
            "thumbnail_url": artwork.thumbnail_url,
            "source": artwork.source,
            "status": artwork.status,
            "created_at": artwork.created_at.isoformat() if artwork.created_at else "",
        }
    )


@router.delete("/{artwork_id}", summary="删除画作")
async def delete_artwork(
    artwork_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除画作（同时删除关联的动画记录）"""
    artwork = (
        db.query(Artwork)
        .filter(Artwork.id == artwork_id, Artwork.user_id == current_user.id)
        .first()
    )
    if not artwork:
        return error("画作不存在或无权限", code=404)

    db.delete(artwork)
    db.commit()

    return success(message="已删除")


@router.post("/batch-delete", summary="批量删除")
async def batch_delete(
    ids: list[int],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """批量删除画作"""
    db.query(Artwork).filter(
        Artwork.id.in_(ids), Artwork.user_id == current_user.id
    ).delete(synchronize_session=False)
    db.commit()

    return success(message=f"已批量删除 {len(ids)} 幅画作")


@router.post("/{artwork_id}/analyze", summary="分析画作并推荐风格")
async def analyze_artwork(
    artwork_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """分析画作内容并推荐动画风格"""
    artwork = (
        db.query(Artwork)
        .filter(Artwork.id == artwork_id, Artwork.user_id == current_user.id)
        .first()
    )
    if not artwork:
        return error("画作不存在或无权限", code=404)

    image_url = artwork.processed_url or artwork.original_url
    if not image_url:
        return error("作品图片不存在", code=400)

    result = AIService.analyze_image(image_url)
    if result is None:
        return error("画作分析失败", code=500)

    # 将推荐风格ID转为包含名称和图标的信息
    templates = (
        db.query(PromptTemplate)
        .filter(PromptTemplate.style_code.in_(result["recommended_styles"]))
        .all()
    )
    template_map = {t.style_code: t for t in templates}

    styles_info = []
    for code in result["recommended_styles"]:
        tmpl = template_map.get(code)
        if tmpl:
            styles_info.append({
                "style_code": code,
                "style_name": tmpl.style_name,
                "icon": tmpl.style_icon,
            })

    return success(data={
        "description": result["description"],
        "recommended_styles": styles_info,
        "detected_animals": result.get("detected_animals", []),
    })
