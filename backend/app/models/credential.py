from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.db.database import Base


class CredentialType(str, enum.Enum):
    ORACLE = "oracle"
    LINUX = "linux"
    FTP = "ftp"
    S3 = "s3"


class Credential(Base):
    __tablename__ = "credentials"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    type = Column(Enum(CredentialType), nullable=False)

    # Connection info (encrypted)
    host = Column(Text, nullable=True)  # Encrypted
    port = Column(Integer, nullable=True)
    username = Column(Text, nullable=True)  # Encrypted
    password = Column(Text, nullable=True)  # Encrypted

    # Extra data (encrypted JSON string)
    # Oracle: service_name, tns
    # Linux: ssh_key
    # FTP: passive_mode
    # S3: endpoint, access_key, secret_key, bucket, region
    extra_data = Column(Text, nullable=True)  # Encrypted JSON

    # Organization
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    tags = Column(JSON, default=list)
    description = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    category = relationship("Category", back_populates="credentials")
    audit_logs = relationship("AuditLog", back_populates="credential", cascade="all, delete-orphan")
