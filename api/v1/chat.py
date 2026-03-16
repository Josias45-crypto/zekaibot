from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from core.database import get_db
from services.chat_service import ChatService
import uuid

router = APIRouter(prefix="/chat", tags=["Chatbot"])


class ChatMessage(BaseModel):
    content: str
    channel: str = "web"


class ChatResponse(BaseModel):
    conversation_id: str
    message: str
    intent: str
    confidence: float
    escalated: bool
    ticket_code: Optional[str] = None


@router.post("/message", response_model=ChatResponse)
def send_message(
    data: ChatMessage,
    db: Session = Depends(get_db),
    x_session_token: Optional[str] = Header(default=None),
    x_user_id: Optional[str] = Header(default=None)
):
    """
    Endpoint principal del chatbot.
    
    Headers opcionales:
    - x-session-token: token de sesión (se genera uno si no existe)
    - x-user-id: ID del usuario autenticado (opcional para anónimos)
    
    El cliente guarda el x-session-token en localStorage
    y lo envía en cada mensaje para mantener el contexto.
    """
    # Generar token de sesión si no viene en el header
    session_token = x_session_token or str(uuid.uuid4())

    result = ChatService(db).process_message(
        content=data.content,
        session_token=session_token,
        user_id=x_user_id,
        channel=data.channel
    )

    return result


@router.get("/history/{conversation_id}")
def get_history(
    conversation_id: str,
    db: Session = Depends(get_db)
):
    """Retorna el historial completo de una conversación."""
    return ChatService(db).get_conversation_history(conversation_id)
