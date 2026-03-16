from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from core.config import settings

# Motor de conexión a PostgreSQL
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,         # verifica conexión antes de usarla
    pool_size=10,               # conexiones simultáneas en el pool
    max_overflow=20,            # conexiones extra en picos de tráfico
    echo=settings.DEBUG         # muestra SQL en consola si DEBUG=True
)

# Fábrica de sesiones
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Clase base para todos los modelos ORM
Base = declarative_base()


def get_db():
    """
    Dependencia de FastAPI — inyecta la sesión de BD en cada endpoint.
    Garantiza que la sesión se cierra aunque ocurra un error.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_connection():
    """Verifica que la conexión a PostgreSQL funciona al arrancar."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Conexión a PostgreSQL exitosa")
        return True
    except Exception as e:
        print(f"❌ Error conectando a PostgreSQL: {e}")
        return False
