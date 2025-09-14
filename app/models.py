from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, Float, DateTime, Text, JSON, Boolean

class Base(DeclarativeBase):
    pass

class ConversationLog(Base):
    __tablename__ = "conversation_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    call_sid: Mapped[str] = mapped_column(String(64))
    session_id: Mapped[str] = mapped_column(String(64))
    from_number: Mapped[str] = mapped_column(String(32))
    to_number: Mapped[str] = mapped_column(String(32))
    transcript: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Appointment(Base):
    __tablename__ = "appointments"
    id: Mapped[int] = mapped_column(primary_key=True)
    customer_name: Mapped[str] = mapped_column(String(128))
    phone: Mapped[str] = mapped_column(String(32))
    email: Mapped[str] = mapped_column(String(256))
    datetime_iso: Mapped[str] = mapped_column(String(64))
    origin_addr: Mapped[str] = mapped_column(Text)
    destination_addr: Mapped[str] = mapped_column(Text)
    notes: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(32), default="scheduled")

class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    ext_ref: Mapped[str] = mapped_column(String(64), index=True)
    customer_name: Mapped[str] = mapped_column(String(128))
    status: Mapped[str] = mapped_column(String(64))
    eta: Mapped[str] = mapped_column(String(64), default="")
    notes: Mapped[str] = mapped_column(Text, default="")

class PricingRules(Base):
    __tablename__ = "pricing_rules"
    id: Mapped[int] = mapped_column(primary_key=True)
    base_fee: Mapped[float] = mapped_column(Float, default=129.0)
    per_mile: Mapped[float] = mapped_column(Float, default=2.5)
    per_room: Mapped[float] = mapped_column(Float, default=85.0)
    stairs_fee: Mapped[float] = mapped_column(Float, default=75.0)
    piano_fee: Mapped[float] = mapped_column(Float, default=200.0)
    weekend_multiplier: Mapped[float] = mapped_column(Float, default=1.15)

class FAQ(Base):
    __tablename__ = "faqs"
    id: Mapped[int] = mapped_column(primary_key=True)
    question: Mapped[str] = mapped_column(Text)
    answer: Mapped[str] = mapped_column(Text)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
