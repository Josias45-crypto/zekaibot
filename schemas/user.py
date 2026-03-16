from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from uuid import UUID
from datetime import datetime


# ── REQUEST SCHEMAS (lo que recibe la API) ──

class UserRegister(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    phone: Optional[str] = None

    @field_validator("password")
    def password_min_length(cls, v):
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        return v

    @field_validator("full_name")
    def full_name_not_empty(cls, v):
        if not v.strip():
            raise ValueError("El nombre no puede estar vacío")
        return v.strip()


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class PasswordChange(BaseModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
    def password_min_length(cls, v):
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        return v


# ── RESPONSE SCHEMAS (lo que devuelve la API) ──

class RoleResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id: UUID
    full_name: str
    email: Optional[str]
    phone: Optional[str]
    is_active: bool
    created_at: datetime
    role: RoleResponse

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class MessageResponse(BaseModel):
    message: str
    success: bool = True
