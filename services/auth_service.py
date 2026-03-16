from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models.user import User
from repositories.user_repo import UserRepository
from core.security import hash_password, verify_password, create_access_token
from schemas.user import UserRegister, UserLogin, TokenResponse, UserResponse


class AuthService:

    def __init__(self, db: Session):
        self.db = db
        self.repo = UserRepository(db)

    def register(self, data: UserRegister) -> TokenResponse:
        # Verificar que el email no exista
        if self.repo.email_exists(data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este correo ya está registrado"
            )

        # Obtener rol de cliente por defecto
        role = self.repo.get_role_by_name("cliente")
        if not role:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error de configuración del sistema"
            )

        # Crear usuario con contraseña hasheada
        user = self.repo.create(
            full_name=data.full_name,
            email=data.email,
            password_hash=hash_password(data.password),
            role_id=role.id,
            phone=data.phone
        )

        # Generar token JWT
        token = create_access_token({"sub": str(user.id), "role": role.name})

        return TokenResponse(
            access_token=token,
            user=UserResponse.model_validate(user)
        )

    def login(self, data: UserLogin) -> TokenResponse:
        # Buscar usuario por email
        user = self.repo.get_by_email(data.email)

        # Verificar credenciales (mismo mensaje para email y password — seguridad)
        if not user or not verify_password(data.password, user.password_hash or ""):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario desactivado"
            )

        # Actualizar último login
        self.repo.update_last_login(user)

        # Generar token
        token = create_access_token({"sub": str(user.id), "role": user.role.name})

        return TokenResponse(
            access_token=token,
            user=UserResponse.model_validate(user)
        )

    def get_current_user(self, user_id: str) -> User:
        user = self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        return user
