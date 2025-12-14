from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from app.models.audit_log import AuditAction


class AuditLogResponse(BaseModel):
    id: int
    credential_id: Optional[int] = None
    credential_name: Optional[str] = None
    action: AuditAction
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AuditLogListResponse(BaseModel):
    items: list[AuditLogResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
