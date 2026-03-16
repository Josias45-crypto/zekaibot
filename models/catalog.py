import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, Integer, Numeric, Date
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base


class Category(Base):
    __tablename__ = "categories"

    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parent_id   = Column(UUID(as_uuid=True), ForeignKey("categories.id"))
    name        = Column(String(100), nullable=False)
    slug        = Column(String(120), unique=True, nullable=False)
    description = Column(Text)
    is_active   = Column(Boolean, nullable=False, default=True)
    created_at  = Column(DateTime, nullable=False, server_default=func.now())

    # Relaciones
    parent   = relationship("Category", remote_side="Category.id", back_populates="children")
    children = relationship("Category", back_populates="parent")
    products = relationship("Product", back_populates="category")


class Brand(Base):
    __tablename__ = "brands"

    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name       = Column(String(100), unique=True, nullable=False)
    country    = Column(String(60))
    logo_url   = Column(Text)
    is_active  = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # Relaciones
    products = relationship("Product", back_populates="brand")


class Product(Base):
    __tablename__ = "products"

    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=False)
    brand_id    = Column(UUID(as_uuid=True), ForeignKey("brands.id"), nullable=False)
    sku         = Column(String(100), unique=True, nullable=False)
    name        = Column(String(200), nullable=False)
    model       = Column(String(100))
    description = Column(Text)
    price       = Column(Numeric(10, 2), nullable=False, default=0)
    image_url   = Column(Text)
    is_active   = Column(Boolean, nullable=False, default=True)
    created_at  = Column(DateTime, nullable=False, server_default=func.now())
    updated_at  = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relaciones
    category    = relationship("Category", back_populates="products")
    brand       = relationship("Brand", back_populates="products")
    specs       = relationship("ProductSpec", back_populates="product", cascade="all, delete-orphan")
    inventory   = relationship("Inventory", back_populates="product", uselist=False)
    drivers     = relationship("Driver", back_populates="product")
    known_issues = relationship("KnownIssue", back_populates="product")
    order_items = relationship("OrderItem", back_populates="product")


class ProductSpec(Base):
    __tablename__ = "product_specs"

    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    spec_key   = Column(String(100), nullable=False)
    spec_value = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # Relaciones
    product = relationship("Product", back_populates="specs")


class Inventory(Base):
    __tablename__ = "inventory"

    id           = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id   = Column(UUID(as_uuid=True), ForeignKey("products.id"), unique=True, nullable=False)
    stock        = Column(Integer, nullable=False, default=0)
    min_stock    = Column(Integer, nullable=False, default=5)
    location     = Column(String(100))
    restock_date = Column(Date)
    updated_at   = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relaciones
    product = relationship("Product", back_populates="inventory")


class Compatibility(Base):
    __tablename__ = "compatibility"

    id            = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id_a  = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    product_id_b  = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    is_compatible = Column(Boolean, nullable=False, default=True)
    notes         = Column(Text)
    created_at    = Column(DateTime, nullable=False, server_default=func.now())
