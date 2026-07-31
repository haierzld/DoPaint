"""
配额管理服务
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.organization import Organization
from loguru import logger


class QuotaService:
    """配额管理"""

    def __init__(self, db: Session):
        self.db = db

    def get_remaining(self, user: User) -> int:
        """
        获取用户剩余配额
        优先级：机构配额 > 个人配额
        """
        if user.org_id:
            org = self.db.query(Organization).filter(Organization.id == user.org_id).first()
            if org and org.plan_type != "free":
                self._check_reset_org(org)
                return org.monthly_quota - org.used_quota

        self._check_reset_personal(user)
        return user.personal_quota - user.personal_used

    def consume(self, user: User, count: int = 1) -> bool:
        """消耗配额，返回是否成功"""
        if self.get_remaining(user) < count:
            return False

        if user.org_id:
            org = self.db.query(Organization).filter(
                Organization.id == user.org_id,
                Organization.plan_type != "free",
            ).first()
            if org:
                org.used_quota += count
                self.db.commit()
                return True

        user.personal_used += count
        self.db.commit()
        return True

    def _check_reset_org(self, org: Organization):
        """检查并重置机构月配额"""
        now = datetime.utcnow()
        if org.quota_reset_at and org.quota_reset_at < now:
            org.used_quota = 0
            org.quota_reset_at = now.replace(day=1) + timedelta(days=32)
            org.quota_reset_at = org.quota_reset_at.replace(day=1)
            self.db.commit()
            logger.info(f"机构 {org.id} 配额已重置")

    def _check_reset_personal(self, user: User):
        """检查并重置个人月配额"""
        now = datetime.utcnow()
        if user.last_login_at and user.last_login_at.month != now.month:
            user.personal_used = 0
            self.db.commit()
