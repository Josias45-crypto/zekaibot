from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime
import uuid
from models.all_models import Conversation, Message, Intent, MessageIntent, Ticket, Escalation
from models.user import Session as UserSession
from services.ai.claude import get_ai_response, parse_intent
from core.config import settings


class ChatService:

    def __init__(self, db: Session):
        self.db = db

    def process_message(self, content: str, session_token: str,
                        user_id: str = None, channel: str = "web") -> dict:
        """
        Flujo completo de un mensaje:
        1. Obtiene o crea la conversación
        2. Guarda el mensaje del usuario
        3. Obtiene historial para contexto
        4. Llama a Claude API
        5. Parsea intención y entidades
        6. Guarda respuesta del bot
        7. Crea ticket si es necesario
        8. Retorna respuesta al cliente
        """

        # 1. Obtener o crear conversación activa
        conversation = self._get_or_create_conversation(
            session_token, user_id, channel
        )

        # 2. Guardar mensaje del usuario
        user_message = Message(
            conversation_id=conversation.id,
            sender_type="user",
            sender_id=user_id,
            content=content
        )
        self.db.add(user_message)
        self.db.flush()

        # 3. Obtener historial de la conversación para contexto
        history = self._get_history(conversation.id)

        # 4. Llamar a Claude API
        try:
            ai_response = get_ai_response(history)
        except Exception as e:
            # RNF-13: degradación elegante ante fallo de IA
            ai_response = "[INTENT: consulta_general | CONF: 0.50 | ESCALATE: true]\nLo siento, estoy teniendo dificultades técnicas en este momento. Un agente humano te atenderá pronto."

        # 5. Parsear intención
        parsed = parse_intent(ai_response)

        # 6. Guardar respuesta del bot
        bot_message = Message(
            conversation_id=conversation.id,
            sender_type="bot",
            content=parsed["clean_text"],
            is_fallback="ESCALATE: true" in ai_response and "dificultades" in ai_response
        )
        self.db.add(bot_message)

        # 7. Registrar intención detectada
        intent_obj = self._get_intent_by_name(parsed["intent"])
        if intent_obj:
            msg_intent = MessageIntent(
                message_id=user_message.id,
                intent_id=intent_obj.id,
                confidence=parsed["confidence"],
                detected_entities={}
            )
            self.db.add(msg_intent)

        # 8. Escalar si es necesario
        ticket_code = None
        if parsed["escalate"] or parsed["confidence"] < settings.DEFAULT_CONFIDENCE_THRESHOLD:
            ticket_code = self._create_ticket(conversation, parsed["intent"], channel)
            conversation.status = "escalated"
        else:
            conversation.status = "active"

        self.db.commit()

        return {
            "conversation_id": str(conversation.id),
            "message": parsed["clean_text"],
            "intent": parsed["intent"],
            "confidence": parsed["confidence"],
            "escalated": parsed["escalate"],
            "ticket_code": ticket_code
        }

    def _get_or_create_conversation(self, session_token: str,
                                     user_id: str, channel: str) -> Conversation:
        """Busca conversación activa o crea una nueva."""
        # Buscar sesión
        session = self.db.execute(
            select(UserSession).where(UserSession.token == session_token)
        ).scalar_one_or_none()

        if not session:
            # Crear sesión anónima
            session = UserSession(
                user_id=user_id,
                token=session_token,
                channel=channel,
                expires_at=datetime.utcnow().replace(year=datetime.utcnow().year + 1)
            )
            self.db.add(session)
            self.db.flush()

        # Buscar conversación activa
        conversation = self.db.execute(
            select(Conversation).where(
                Conversation.session_id == session.id,
                Conversation.status == "active"
            )
        ).scalar_one_or_none()

        if not conversation:
            conversation = Conversation(
                session_id=session.id,
                user_id=user_id,
                channel=channel,
                status="active"
            )
            self.db.add(conversation)
            self.db.flush()

        return conversation

    def _get_history(self, conversation_id) -> list[dict]:
        """Obtiene el historial de mensajes en formato para Claude API."""
        messages = self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
            .limit(settings.CHAT_HISTORY_LIMIT)
        ).scalars().all()

        history = []
        for msg in messages:
            role = "user" if msg.sender_type == "user" else "assistant"
            history.append({"role": role, "content": msg.content})
        return history

    def _get_intent_by_name(self, name: str):
        return self.db.execute(
            select(Intent).where(Intent.name == name)
        ).scalar_one_or_none()

    def _create_ticket(self, conversation: Conversation,
                       category: str, channel: str) -> str:
        """Crea ticket automático cuando se escala."""
        # Verificar si ya existe ticket para esta conversación
        existing = self.db.execute(
            select(Ticket).where(Ticket.conversation_id == conversation.id)
        ).scalar_one_or_none()

        if existing:
            return existing.reference_code

        # Generar código único TK-YYYY-NNNNN
        year = datetime.utcnow().year
        count = self.db.query(Ticket).count() + 1
        reference_code = f"TK-{year}-{count:05d}"

        ticket = Ticket(
            conversation_id=conversation.id,
            user_id=conversation.user_id,
            reference_code=reference_code,
            category=category if category in [
                'precio', 'compatibilidad', 'driver',
                'error_tecnico', 'reparacion', 'pedido', 'general'
            ] else 'general',
            priority="medium",
            status="open",
            channel_origin=channel
        )
        self.db.add(ticket)

        # Registrar escalamiento
        escalation = Escalation(
            conversation_id=conversation.id,
            reason="low_confidence",
            escalated_at=datetime.utcnow()
        )
        self.db.add(escalation)
        self.db.flush()

        return reference_code

    def get_conversation_history(self, conversation_id: str) -> list[dict]:
        """Retorna historial completo de una conversación."""
        messages = self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
        ).scalars().all()

        return [
            {
                "sender": msg.sender_type,
                "content": msg.content,
                "time": msg.created_at.isoformat()
            }
            for msg in messages
        ]
