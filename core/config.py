from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # ── App ──
    APP_NAME: str = "TechBot"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # ── Base de datos ──
    DATABASE_URL: str

    # ── Redis ──
    REDIS_URL: str = "redis://localhost:6379"

    # ── Seguridad ──
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # ── Claude API ──
    ANTHROPIC_API_KEY: str = "no-se-usa"
    GOOGLE_API_KEY: str = ""

    # ── Configuración del chatbot ──
    DEFAULT_CONFIDENCE_THRESHOLD: float = 0.70
    MAX_TOKENS_RESPONSE: int = 1000
    CHAT_HISTORY_LIMIT: int = 20        # mensajes a mantener en contexto

    # ── Rate limiting ──
    RATE_LIMIT_CHAT: int = 60           # mensajes por hora por IP
    RATE_LIMIT_LOGIN: int = 10          # intentos de login por hora

    class Config:
        env_file = ".env"
        case_sensitive = True


# Instancia global — se importa en todo el proyecto
settings = Settings()
