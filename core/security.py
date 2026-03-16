from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from core.config import settings

# Contexto de encriptación — bcrypt con factor 12 (RNF-17)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Convierte contraseña en texto plano a hash bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si una contraseña coincide con su hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Genera un JWT firmado con los datos del usuario.
    El token expira según ACCESS_TOKEN_EXPIRE_MINUTES del .env
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decodifica y valida un JWT.
    Retorna el payload si es válido, None si expiró o es inválido.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def create_anonymous_token(session_id: str) -> str:
    """
    Genera un token para sesiones anónimas (RF-01).
    No tiene expiración fija — expira cuando la sesión se cierra.
    """
    data = {
        "session_id": session_id,
        "type": "anonymous",
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
