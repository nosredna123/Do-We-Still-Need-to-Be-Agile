from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    Enum as SQLAlchemyEnum,
    CheckConstraint,
    JSON,
    text, Date,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database.base import Base
from src.utils.enums import ChatRole, TransactionType, ToolName, RecurrenceFrequency


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    profile_pic = Column(String, nullable=True)
    api_key = Column(String, nullable=True)
    salary_recurrence_id = Column(Integer, ForeignKey("recurrent_transactions.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=True)
    updated_at = Column(DateTime, onupdate=func.now(), nullable=True)
    transactions = relationship("Transaction", back_populates="user")
    chat_sessions = relationship("ChatSession", back_populates="user")
    salary_recurrence = relationship("RecurrentTransaction", foreign_keys=[salary_recurrence_id], post_update=True)


class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    transactions = relationship("Transaction", back_populates="category")
    created_at = Column(DateTime, server_default=func.now(), nullable=True)
    updated_at = Column(DateTime, onupdate=func.now(), nullable=True)


class RecurrentTransaction(Base):
    __tablename__ = "recurrent_transactions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    base_transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=False)
    frequency = Column(
        SQLAlchemyEnum(
            RecurrenceFrequency,
            values_callable=lambda obj: [e.value for e in obj]
        ),
        default=RecurrenceFrequency.MONTHLY,
        nullable=False
    )
    recurrence_day = Column(Integer, nullable=False, comment="Day of the month (1-31)")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=True)
    updated_at = Column(DateTime, onupdate=func.now(), nullable=True)
    base_transaction = relationship("Transaction", foreign_keys=[base_transaction_id])
    generated_transactions = relationship("Transaction", back_populates="created_by_recurrence", foreign_keys="Transaction.created_by_recurrence_id")


class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Integer, nullable=False)
    description = Column(Text, nullable=False)
    reference_date = Column(Date, nullable=False, default=func.current_date(), index=True)
    transaction_type = Column(
        SQLAlchemyEnum(
            TransactionType,
            values_callable=lambda obj: [e.value for e in obj]
        ),
        nullable=False
    )
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_by_recurrence_id = Column(Integer, ForeignKey("recurrent_transactions.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=True)
    updated_at = Column(DateTime, onupdate=func.now(), nullable=True)
    user = relationship("User", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")
    created_by_recurrence = relationship("RecurrentTransaction", back_populates="generated_transactions", foreign_keys=[created_by_recurrence_id])
    __table_args__ = (
        CheckConstraint(
            "(transaction_type = 'income' AND category_id IS NULL) OR "
            "(transaction_type = 'expense' AND category_id IS NOT NULL)",
            name="ck_transaction_attributes",
        ),
    )


class ChatSession(Base):
    __tablename__ = "chat_sessions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=True)
    updated_at = Column(DateTime, onupdate=func.now(), nullable=True)
    pending_tool = Column(
        SQLAlchemyEnum(
            ToolName,
            values_callable=lambda obj: [e.value for e in obj]
        ),
        nullable=True,
        default=None,
        index=True
    )
    collected_params = Column(
        JSON,
        nullable=False,
        server_default=text("'{}'")
    )
    missing_fields = Column(
        JSON,
        nullable=False,
        server_default=text("'[]'")
    )
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship(
        "ChatMessage", back_populates="session", cascade="all, delete-orphan"
    )


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(
        SQLAlchemyEnum(
            ChatRole,
            values_callable=lambda obj: [e.value for e in obj]
        ),
        nullable=False
    )
    content = Column(Text, nullable=False)
    meta_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=True)
    session = relationship("ChatSession", back_populates="messages")