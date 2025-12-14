from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.db.database import Base


class AuditAction(str, enum.Enum):
    VIEW = "view"
    COPY = "copy"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    credential_id = Column(Integer, ForeignKey("credentials.id", ondelete="CASCADE"), nullable=True)
    credential_name = Column(String(100), nullable=True)  # Store name for deleted credentials
    action = Column(Enum(AuditAction), nullable=False)
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    credential = relationship("Credential", back_populates="audit_logs")
