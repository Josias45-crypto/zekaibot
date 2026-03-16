from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.database import get_db
from api.deps import get_current_user
from services.auth_service import AuthService
from schemas.user import UserRegister, UserLogin, TokenResponse, UserResponse
from models.user import User

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(data: UserRegister, db: Session = Depends(get_db)):
    """
    Registra un nuevo cliente.
    Devuelve el token JWT listo para usar.
    """
    return AuthService(db).register(data)


@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    """
    Inicia sesión con email y contraseña.
    Devuelve el token JWT.
    """
    return AuthService(db).login(data)


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    """
    Devuelve los datos del usuario autenticado.
    Requiere token JWT en el header: Authorization: Bearer <token>
    """
    return current_user
