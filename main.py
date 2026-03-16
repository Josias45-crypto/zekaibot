from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from core.database import check_connection
from api.v1.router import router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Sistema Inteligente de Atención al Cliente",
    docs_url="/docs",       # Swagger UI en /docs
    redoc_url="/redoc"      # ReDoc en /redoc
)

# CORS — permite que el widget de la web se conecte al backend
app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    # en producción: solo el dominio de la empresa
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    """Se ejecuta al arrancar el servidor."""
    print(f"🚀 Iniciando {settings.APP_NAME} v{settings.APP_VERSION}")
    check_connection()


@app.get("/")
def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
def health():
    """Endpoint de salud — para monitoreo del servidor."""
    return {"status": "ok"}
