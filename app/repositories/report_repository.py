from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit_log import AuditLog
import uuid


class ReportRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def log_audit(self, user_id: str, action: str, resource_type: str = None, resource_id: str = None, details: dict = None) -> AuditLog:
        log = AuditLog(
            id=str(uuid.uuid4()),
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
        )
        self.db.add(log)
        await self.db.flush()
        return log
