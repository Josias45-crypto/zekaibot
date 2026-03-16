import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base


class Role(Base):
    __tablename__ = "roles"

    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name        = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    permissions = Column(JSONB, nullable=False, default=list)
    is_active   = Column(Boolean, nullable=False, default=True)
    created_at  = Column(DateTime, nullable=False, server_default=func.now())

    # Relaciones
    users = relationship("User", back_populates="role")


class User(Base):
    __tablename__ = "users"

    id            = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_id       = Column(UUID(as_uuid=True), ForeignKey("roles.id"), nullable=False)
    full_name     = Column(String(100), nullable=False)
    email         = Column(String(150), unique=True)
    phone         = Column(String(20))
    password_hash = Column(String(255))
    is_active     = Column(Boolean, nullable=False, default=True)
    last_login    = Column(DateTime)
    created_at    = Column(DateTime, nullable=False, server_default=func.now())
    updated_at    = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relaciones
    role          = relationship("Role", back_populates="users")
    sessions      = relationship("Session", back_populates="user")
    conversations = relationship("Conversation", foreign_keys="Conversation.user_id", back_populates="user")
    tickets       = relationship("Ticket", back_populates="user")
    orders        = relationship("Order", back_populates="user")
    repairs       = relationship("Repair", foreign_keys="Repair.user_id", back_populates="user")


class Session(Base):
    __tablename__ = "sessions"

    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id    = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    token      = Column(String(500), unique=True, nullable=False)
    channel    = Column(String(20), nullable=False)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    is_active  = Column(Boolean, nullable=False, default=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # Relaciones
    user          = relationship("User", back_populates="sessions")
    conversations = relationship("Conversation", back_populates="session")
