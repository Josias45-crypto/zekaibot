import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, Integer, Numeric, Date
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base


# ── CONOCIMIENTO ──────────────────────────────────────────

class Driver(Base):
    __tablename__ = "drivers"

    id               = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id       = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    name             = Column(String(200), nullable=False)
    version          = Column(String(50))
    operating_system = Column(String(80), nullable=False)
    architecture     = Column(String(10), nullable=False)
    download_url     = Column(Text)
    release_date     = Column(Date)
    is_active        = Column(Boolean, nullable=False, default=True)
    created_at       = Column(DateTime, nullable=False, server_default=func.now())

    product = relationship("Product", back_populates="drivers")


class KnownIssue(Base):
    __tablename__ = "known_issues"

    id             = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id     = Column(UUID(as_uuid=True), ForeignKey("products.id"))
    title          = Column(String(200), nullable=False)
    error_code     = Column(String(100))
    description    = Column(Text, nullable=False)
    solution_steps = Column(JSONB, nullable=False, default=list)
    category       = Column(String(50), nullable=False)
    difficulty     = Column(String(20), nullable=False, default="basico")
    is_active      = Column(Boolean, nullable=False, default=True)
    created_at     = Column(DateTime, nullable=False, server_default=func.now())
    updated_at     = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    product = relationship("Product", back_populates="known_issues")


class FAQ(Base):
    __tablename__ = "faqs"

    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question   = Column(Text, nullable=False)
    answer     = Column(Text, nullable=False)
    category   = Column(String(50))
    times_used = Column(Integer, nullable=False, default=0)
    is_active  = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())


class KnowledgeEmbedding(Base):
    __tablename__ = "knowledge_embeddings"

    id           = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_type  = Column(String(50), nullable=False)
    source_id    = Column(UUID(as_uuid=True), nullable=False)
    content_text = Column(Text, nullable=False)
    # El campo vector se maneja directamente con pgvector en queries SQL
    created_at   = Column(DateTime, nullable=False, server_default=func.now())
    updated_at   = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())


# ── CHATBOT ───────────────────────────────────────────────

class Intent(Base):
    __tablename__ = "intents"

    id                   = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name                 = Column(String(100), unique=True, nullable=False)
    description          = Column(Text)
    training_examples    = Column(JSONB, nullable=False, default=list)
    confidence_threshold = Column(Numeric(3, 2), nullable=False, default=0.70)
    is_active            = Column(Boolean, nullable=False, default=True)
    created_at           = Column(DateTime, nullable=False, server_default=func.now())
    updated_at           = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    message_intents = relationship("MessageIntent", back_populates="intent")


class Conversation(Base):
    __tablename__ = "conversations"

    id                = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id        = Column(UUID(as_uuid=True), ForeignKey("sessions.id"), nullable=False)
    user_id           = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    channel           = Column(String(20), nullable=False)
    status            = Column(String(20), nullable=False, default="active")
    assigned_agent_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    resolved_by       = Column(String(10))
    context_summary   = Column(Text)
    started_at        = Column(DateTime, nullable=False, server_default=func.now())
    closed_at         = Column(DateTime)
    created_at        = Column(DateTime, nullable=False, server_default=func.now())

    session    = relationship("Session", back_populates="conversations")
    user       = relationship("User", foreign_keys=[user_id], back_populates="conversations")
    messages   = relationship("Message", back_populates="conversation")
    ticket     = relationship("Ticket", back_populates="conversation", uselist=False)
    escalations = relationship("Escalation", back_populates="conversation")


class Message(Base):
    __tablename__ = "messages"

    id              = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    sender_type     = Column(String(10), nullable=False)
    sender_id       = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    content         = Column(Text, nullable=False)
    extra_data      = Column(JSONB, nullable=False, default=dict)
    is_fallback     = Column(Boolean, nullable=False, default=False)
    created_at      = Column(DateTime, nullable=False, server_default=func.now())

    conversation    = relationship("Conversation", back_populates="messages")
    message_intents = relationship("MessageIntent", back_populates="message")


class MessageIntent(Base):
    __tablename__ = "message_intents"

    id                = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id        = Column(UUID(as_uuid=True), ForeignKey("messages.id"), nullable=False)
    intent_id         = Column(UUID(as_uuid=True), ForeignKey("intents.id"), nullable=False)
    confidence        = Column(Numeric(5, 4), nullable=False)
    detected_entities = Column(JSONB, nullable=False, default=dict)
    created_at        = Column(DateTime, nullable=False, server_default=func.now())

    message = relationship("Message", back_populates="message_intents")
    intent  = relationship("Intent", back_populates="message_intents")


class Escalation(Base):
    __tablename__ = "escalations"

    id              = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    reason          = Column(String(50), nullable=False)
    confidence_score = Column(Numeric(5, 4))
    agent_id        = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    escalated_at    = Column(DateTime, nullable=False, server_default=func.now())
    attended_at     = Column(DateTime)
    resolved_at     = Column(DateTime)

    conversation = relationship("Conversation", back_populates="escalations")


# ── TICKETS ───────────────────────────────────────────────

class Ticket(Base):
    __tablename__ = "tickets"

    id              = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    user_id         = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    reference_code  = Column(String(20), unique=True, nullable=False)
    category        = Column(String(50), nullable=False)
    priority        = Column(String(20), nullable=False, default="medium")
    status          = Column(String(20), nullable=False, default="open")
    resolved_by     = Column(String(10))
    channel_origin  = Column(String(20), nullable=False)
    notes           = Column(Text)
    created_at      = Column(DateTime, nullable=False, server_default=func.now())
    updated_at      = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    closed_at       = Column(DateTime)

    conversation = relationship("Conversation", back_populates="ticket")
    user         = relationship("User", back_populates="tickets")
    history      = relationship("TicketHistory", back_populates="ticket")


class TicketHistory(Base):
    __tablename__ = "ticket_history"

    id              = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_id       = Column(UUID(as_uuid=True), ForeignKey("tickets.id"), nullable=False)
    previous_status = Column(String(20))
    new_status      = Column(String(20), nullable=False)
    changed_by_id   = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    note            = Column(Text)
    created_at      = Column(DateTime, nullable=False, server_default=func.now())

    ticket = relationship("Ticket", back_populates="history")


# ── PEDIDOS Y REPARACIONES ────────────────────────────────

class Order(Base):
    __tablename__ = "orders"

    id             = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id        = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    reference_code = Column(String(20), unique=True, nullable=False)
    status         = Column(String(20), nullable=False, default="pending")
    total          = Column(Numeric(10, 2), nullable=False, default=0)
    channel_origin = Column(String(20), nullable=False)
    notes          = Column(Text)
    created_at     = Column(DateTime, nullable=False, server_default=func.now())
    updated_at     = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    user  = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id   = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    quantity   = Column(Integer, nullable=False, default=1)
    unit_price = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    order   = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")


class Repair(Base):
    __tablename__ = "repairs"

    id                  = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id             = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    technician_id       = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    reference_code      = Column(String(20), unique=True, nullable=False)
    type                = Column(String(10), nullable=False, default="physical")
    device_description  = Column(Text, nullable=False)
    problem_description = Column(Text, nullable=False)
    diagnosis           = Column(Text)
    status              = Column(String(30), nullable=False, default="received")
    estimated_cost      = Column(Numeric(10, 2))
    final_cost          = Column(Numeric(10, 2))
    estimated_delivery  = Column(Date)
    actual_delivery     = Column(Date)
    created_at          = Column(DateTime, nullable=False, server_default=func.now())
    updated_at          = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    user       = relationship("User", foreign_keys=[user_id], back_populates="repairs")
    technician = relationship("User", foreign_keys=[technician_id])
    history    = relationship("RepairHistory", back_populates="repair")


class RepairHistory(Base):
    __tablename__ = "repair_history"

    id              = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    repair_id       = Column(UUID(as_uuid=True), ForeignKey("repairs.id"), nullable=False)
    previous_status = Column(String(30))
    new_status      = Column(String(30), nullable=False)
    technical_note  = Column(Text)
    changed_by_id   = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at      = Column(DateTime, nullable=False, server_default=func.now())

    repair = relationship("Repair", back_populates="history")


# ── AUDITORÍA ─────────────────────────────────────────────

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id     = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    action      = Column(String(100), nullable=False)
    entity_type = Column(String(50))
    entity_id   = Column(UUID(as_uuid=True))
    detail      = Column(JSONB, nullable=False, default=dict)
    ip_address  = Column(String(45))
    channel     = Column(String(20))
    created_at  = Column(DateTime, nullable=False, server_default=func.now())


class MetricsDaily(Base):
    __tablename__ = "metrics_daily"

    id                    = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date                  = Column(Date, unique=True, nullable=False)
    total_conversations   = Column(Integer, nullable=False, default=0)
    resolved_by_bot       = Column(Integer, nullable=False, default=0)
    resolved_by_agent     = Column(Integer, nullable=False, default=0)
    escalated             = Column(Integer, nullable=False, default=0)
    abandoned             = Column(Integer, nullable=False, default=0)
    avg_response_time_sec = Column(Numeric(6, 2))
    avg_resolution_min    = Column(Numeric(8, 2))
    top_intent            = Column(String(100))
    unresolved_queries    = Column(JSONB, nullable=False, default=list)
    by_channel            = Column(JSONB, nullable=False, default=dict)
    by_category           = Column(JSONB, nullable=False, default=dict)
    tokens_consumed       = Column(Integer, nullable=False, default=0)
    estimated_cost_usd    = Column(Numeric(8, 4))
    created_at            = Column(DateTime, nullable=False, server_default=func.now())
