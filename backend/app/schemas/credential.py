from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

from app.models.credential import CredentialType


# Oracle specific fields
class OracleExtra(BaseModel):
    service_name: Optional[str] = None
    tns: Optional[str] = None


# Linux specific fields
class LinuxExtra(BaseModel):
    ssh_key: Optional[str] = None


# FTP specific fields
class FTPExtra(BaseModel):
    passive_mode: bool = True


# S3 specific fields
class S3Extra(BaseModel):
    endpoint: Optional[str] = None
    access_key: Optional[str] = None
    secret_key: Optional[str] = None
    bucket: Optional[str] = None
    region: Optional[str] = None


# Base credential schema
class CredentialBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    type: CredentialType
    host: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    extra_data: Optional[dict] = None
    category_id: Optional[int] = None
    tags: list[str] = []
    description: Optional[str] = None


class CredentialCreate(CredentialBase):
    pass


class CredentialUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    type: Optional[CredentialType] = None
    host: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    extra_data: Optional[dict] = None
    category_id: Optional[int] = None
    tags: Optional[list[str]] = None
    description: Optional[str] = None


class CredentialResponse(CredentialBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    category_name: Optional[str] = None
    category_color: Optional[str] = None

    class Config:
        from_attributes = True


class CredentialListResponse(BaseModel):
    items: list[CredentialResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
