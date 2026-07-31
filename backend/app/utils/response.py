"""
统一响应格式
"""
from typing import Any


def success(data: Any = None, message: str = "操作成功") -> dict:
    """成功响应"""
    return {"code": 0, "message": message, "data": data}


def paginated(items: list, total: int, page: int, page_size: int) -> dict:
    """分页响应"""
    return {
        "code": 0,
        "message": "操作成功",
        "data": {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size if page_size > 0 else 0,
        },
    }


def error(message: str = "操作失败", code: int = -1) -> dict:
    """错误响应"""
    return {"code": code, "message": message, "data": None}
