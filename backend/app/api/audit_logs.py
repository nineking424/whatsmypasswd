from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import math

from app.db.database import get_db
from app.api.auth import verify_token
from app.models import AuditLog, AuditAction
from app.schemas.audit_log import AuditLogResponse, AuditLogListResponse

router = APIRouter(prefix="/audit-logs", tags=["audit-logs"])


@router.get("", response_model=AuditLogListResponse)
async def list_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    action: Optional[AuditAction] = None,
    credential_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_token),
):
    """List audit logs with pagination and filters."""
    query = select(AuditLog)

    # Apply filters
    if action:
        query = query.where(AuditLog.action == action)

    if credential_id:
        query = query.where(AuditLog.credential_id == credential_id)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    # Pagination
    offset = (page - 1) * page_size
    query = query.order_by(AuditLog.created_at.desc())
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    logs = result.scalars().all()

    items = [AuditLogResponse.model_validate(log) for log in logs]
    total_pages = math.ceil(total / page_size) if total else 0

    return AuditLogListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )
