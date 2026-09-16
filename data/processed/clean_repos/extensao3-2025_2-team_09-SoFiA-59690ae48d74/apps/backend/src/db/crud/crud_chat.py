from sqlalchemy.orm import Session
from src.db.models import models
from typing import Optional, Dict, Any, List

from src.db.models.models import ChatSession, ChatMessage


def create_session(
        db: Session, user_id: int, title: str = "New Chat"
) -> models.ChatSession:
    db_session = models.ChatSession(user_id=user_id, title=title)
    db.add(db_session)
    db.flush()
    db.refresh(db_session)
    return db_session


def get_session(
        db: Session, session_id: int, user_id: int
) -> models.ChatSession | None:
    return (
        db.query(models.ChatSession)
        .filter(
            models.ChatSession.id == session_id, models.ChatSession.user_id == user_id
        )
        .first()
    )


def update_session(
        db: Session, session_id: int, user_id: int, title: str
) -> models.ChatSession | None:
    """Updates the title of a chat session."""
    db_session = get_session(db, session_id, user_id)
    if db_session:
        db_session.title = title
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
    return db_session


def delete_session(db: Session, session_id: int, user_id: int) -> bool:
    """Deletes a session and its messages (via cascade). Returns True if deleted."""
    db_session = get_session(db, session_id, user_id)
    if db_session:
        db.delete(db_session)
        db.commit()
        return True
    return False


def add_message(
        db: Session,
        session_id: int,
        role: models.ChatRole,
        content: str,
        meta_data: dict = None,
) -> models.ChatMessage:
    db_message = models.ChatMessage(
        session_id=session_id, role=role, content=content, meta_data=meta_data
    )
    db.add(db_message)
    db.flush()
    db.refresh(db_message)
    return db_message


def get_history(db: Session, session_id: int, limit: int = 20):
    """Retrieves the last N messages for context window."""
    return (
        db.query(models.ChatMessage)
        .filter(models.ChatMessage.session_id == session_id)
        .order_by(models.ChatMessage.created_at.asc())
        .limit(limit)
        .all()
    )


def get_session_state(
        db: Session, session_id: int
) -> Optional[Dict[str, Any]]:
    """
    Retrieves the current conversation state for a session.

    Returns:
        {
            "pending_tool": "expense" | "income" | None,
            "collected_params": {"amount": 12000, "description": "makeup"},
            "missing_fields": ["category_name"]
        }
        or None if session doesn't exist
    """
    session = db.query(models.ChatSession).filter(
        models.ChatSession.id == session_id
    ).first()
    if not session:
        return None
    return {
        "pending_tool": session.pending_tool,
        "collected_params": session.collected_params or {},
        "missing_fields": session.missing_fields or []
    }


def update_session_state(
        db: Session,
        session_id: int,
        pending_tool: Optional[str] = None,
        collected_params: Optional[Dict[str, Any]] = None,
        missing_fields: Optional[List[str]] = None
) -> models.ChatSession:
    """
    Updates the conversation state for multi-turn parameter collection.

    Args:
        session_id: The chat session ID
        pending_tool: Name of the tool waiting for parameters (e.g., "expense")
        collected_params: Partial parameters extracted so far
        missing_fields: List of required fields still needed

    Example:
        update_session_state(
            db,
            session_id=1,
            pending_tool="expense",
            collected_params={"description": "makeup"},
            missing_fields=["amount", "category_name"]
        )
    """
    session = db.query(models.ChatSession).filter(
        models.ChatSession.id == session_id
    ).first()

    if not session:
        raise ValueError(f"Session {session_id} not found")

    if pending_tool is not None:
        session.pending_tool = pending_tool
    if collected_params is not None:
        session.collected_params = collected_params
    if missing_fields is not None:
        session.missing_fields = missing_fields

    db.add(session)
    db.flush()
    db.refresh(session)
    return session


def clear_session_state(db: Session, session_id: int) -> models.ChatSession:
    """
    Clears the conversation state after successful tool execution.
    Resets pending_tool to None and empties collected_params/missing_fields.
    """
    session = db.query(models.ChatSession).filter(
        models.ChatSession.id == session_id
    ).first()

    if not session:
        raise ValueError(f"Session {session_id} not found")

    session.pending_tool = None
    session.collected_params = {}
    session.missing_fields = []

    db.add(session)
    db.flush()
    db.refresh(session)
    return session

def get_user_sessions(
    db: Session, user_id: int, skip: int = 0, limit: int = 10
) -> list[type[ChatSession]]:
    """
    Retrieves a paginated list of chat sessions for a user.
    Ordered by most recent first.
    """
    return (
        db.query(models.ChatSession)
        .filter(models.ChatSession.user_id == user_id)
        .order_by(models.ChatSession.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_session_messages(db: Session, session_id: int):
    """
    Returns the Query object.
    """
    return (
        db.query(models.ChatMessage)
        .filter(models.ChatMessage.session_id == session_id)
        .order_by(models.ChatMessage.created_at.desc())
    )