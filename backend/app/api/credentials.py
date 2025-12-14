from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
import math

from app.db.database import get_db
from app.api.auth import verify_token
from app.models import Credential, Category, AuditLog, AuditAction, CredentialType
from app.schemas.credential import (
    CredentialCreate,
    CredentialUpdate,
    CredentialResponse,
    CredentialListResponse,
)
from app.services.crypto import get_crypto_service

router = APIRouter(prefix="/credentials", tags=["credentials"])
crypto = get_crypto_service()


def encrypt_credential(data: dict) -> dict:
    """Encrypt sensitive fields."""
    encrypted = data.copy()
    if encrypted.get("host"):
        encrypted["host"] = crypto.encrypt(encrypted["host"])
    if encrypted.get("username"):
        encrypted["username"] = crypto.encrypt(encrypted["username"])
    if encrypted.get("password"):
        encrypted["password"] = crypto.encrypt(encrypted["password"])
    if encrypted.get("extra_data"):
        encrypted["extra_data"] = crypto.encrypt_dict(encrypted["extra_data"])
    return encrypted


def decrypt_credential(credential: Credential) -> dict:
    """Decrypt sensitive fields."""
    return {
        "id": credential.id,
        "name": credential.name,
        "type": credential.type,
        "host": crypto.decrypt(credential.host) if credential.host else None,
        "port": credential.port,
        "username": crypto.decrypt(credential.username) if credential.username else None,
        "password": crypto.decrypt(credential.password) if credential.password else None,
        "extra_data": crypto.decrypt_dict(credential.extra_data) if credential.extra_data else None,
        "category_id": credential.category_id,
        "tags": credential.tags or [],
        "description": credential.description,
        "created_at": credential.created_at,
        "updated_at": credential.updated_at,
        "category_name": credential.category.name if credential.category else None,
        "category_color": credential.category.color if credential.category else None,
    }


async def log_audit(
    db: AsyncSession,
    request: Request,
    action: AuditAction,
    credential_id: Optional[int] = None,
    credential_name: Optional[str] = None,
):
    """Log audit event."""
    log = AuditLog(
        credential_id=credential_id,
        credential_name=credential_name,
        action=action,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent", "")[:255],
    )
    db.add(log)
    await db.flush()


@router.get("", response_model=CredentialListResponse)
async def list_credentials(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    type: Optional[CredentialType] = None,
    category_id: Optional[int] = None,
    tags: Optional[str] = None,  # comma separated
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_token),
):
    """List credentials with pagination and filters."""
    query = select(Credential).options(selectinload(Credential.category))

    # Apply filters
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                Credential.name.ilike(search_term),
                Credential.description.ilike(search_term),
            )
        )

    if type:
        query = query.where(Credential.type == type)

    if category_id:
        query = query.where(Credential.category_id == category_id)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    # Pagination
    offset = (page - 1) * page_size
    query = query.order_by(Credential.updated_at.desc().nullsfirst(), Credential.created_at.desc())
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    credentials = result.scalars().all()

    items = [CredentialResponse(**decrypt_credential(c)) for c in credentials]
    total_pages = math.ceil(total / page_size) if total else 0

    return CredentialListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{credential_id}", response_model=CredentialResponse)
async def get_credential(
    credential_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_token),
):
    """Get a single credential by ID."""
    query = (
        select(Credential)
        .options(selectinload(Credential.category))
        .where(Credential.id == credential_id)
    )
    result = await db.execute(query)
    credential = result.scalar_one_or_none()

    if not credential:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Credential not found",
        )

    await log_audit(db, request, AuditAction.VIEW, credential.id, credential.name)

    return CredentialResponse(**decrypt_credential(credential))


@router.post("", response_model=CredentialResponse, status_code=status.HTTP_201_CREATED)
async def create_credential(
    data: CredentialCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_token),
):
    """Create a new credential."""
    encrypted_data = encrypt_credential(data.model_dump())

    credential = Credential(**encrypted_data)
    db.add(credential)
    await db.flush()

    # Reload with category
    query = (
        select(Credential)
        .options(selectinload(Credential.category))
        .where(Credential.id == credential.id)
    )
    result = await db.execute(query)
    credential = result.scalar_one()

    await log_audit(db, request, AuditAction.CREATE, credential.id, credential.name)

    return CredentialResponse(**decrypt_credential(credential))


@router.put("/{credential_id}", response_model=CredentialResponse)
async def update_credential(
    credential_id: int,
    data: CredentialUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_token),
):
    """Update an existing credential."""
    query = (
        select(Credential)
        .options(selectinload(Credential.category))
        .where(Credential.id == credential_id)
    )
    result = await db.execute(query)
    credential = result.scalar_one_or_none()

    if not credential:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Credential not found",
        )

    update_data = data.model_dump(exclude_unset=True)
    encrypted_data = encrypt_credential(update_data)

    for key, value in encrypted_data.items():
        setattr(credential, key, value)

    await db.flush()

    # Reload with category
    query = (
        select(Credential)
        .options(selectinload(Credential.category))
        .where(Credential.id == credential.id)
    )
    result = await db.execute(query)
    credential = result.scalar_one()

    await log_audit(db, request, AuditAction.UPDATE, credential.id, credential.name)

    return CredentialResponse(**decrypt_credential(credential))


@router.delete("/{credential_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_credential(
    credential_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_token),
):
    """Delete a credential."""
    query = select(Credential).where(Credential.id == credential_id)
    result = await db.execute(query)
    credential = result.scalar_one_or_none()

    if not credential:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Credential not found",
        )

    credential_name = credential.name
    await db.delete(credential)

    await log_audit(db, request, AuditAction.DELETE, None, credential_name)


@router.post("/{credential_id}/copy")
async def copy_credential(
    credential_id: int,
    field: str = Query(..., description="Field to copy: password, username, host, etc."),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_token),
):
    """Log a copy action for audit purposes."""
    query = select(Credential).where(Credential.id == credential_id)
    result = await db.execute(query)
    credential = result.scalar_one_or_none()

    if not credential:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Credential not found",
        )

    await log_audit(db, request, AuditAction.COPY, credential.id, f"{credential.name}:{field}")

    return {"success": True}
