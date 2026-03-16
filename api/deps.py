from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import decode_access_token
from models.user import User
from repositories.user_repo import UserRepository

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Extrae y valida el usuario del JWT en cada request."""
    token = credentials.credentials
    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado"
        )

    user = UserRepository(db).get_by_id(payload.get("sub"))
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado o desactivado"
        )
    return user


def require_role(*roles: str):
    """Verifica que el usuario tiene uno de los roles requeridos."""
    def checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role.name not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para esta acción"
            )
        return current_user
    return checker


# Shortcuts para usar en los endpoints
require_admin  = require_role("admin")
require_agent  = require_role("admin", "agente")
require_client = require_role("admin", "agente", "cliente")
