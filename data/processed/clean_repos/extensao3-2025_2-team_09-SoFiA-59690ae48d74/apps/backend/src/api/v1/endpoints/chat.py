from typing import List

from fastapi import APIRouter, status, Depends, HTTPException, Path, Query
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import Session
from src.db.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ChatSessionInit,
    ChatSessionUpdate,
    ChatSessionRead, MessageRead,
)
from src.services.chat_service import ChatService
from src.api.deps import get_chat_service
from src.db.database.connection import get_db
from src.db.crud import crud_chat
from src.utils.constants import APPLICATION_USER_ID

router = APIRouter()


@router.post(
    "/sessions",
    response_model=ChatResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start a new chat session with an initial message",
)
def start_new_session(
    request: ChatSessionInit, service: ChatService = Depends(get_chat_service)
):
    """
    Creates a new conversation thread.

    1. Accepts an initial message and LLM settings.
    2. Generates a title for the session based on the message.
    3. Returns the initial AI response and the created session ID/Title.
    """
    return service.create_session_and_reply(
        message=request.message,
        model_preference=request.model_preference,
        model_name=request.model_name,
    )


@router.put(
    "/sessions/{session_id}",
    response_model=ChatSessionRead,
    status_code=status.HTTP_200_OK,
    summary="Update chat session details (e.g., Title)",
)
def update_session_details(
    update_data: ChatSessionUpdate,
    session_id: int = Path(..., description="The ID of the chat session"),
    db: Session = Depends(get_db),
):
    """
    Updates the title of an existing chat session.
    """
    session = crud_chat.update_session(
        db, session_id=session_id, user_id=APPLICATION_USER_ID, title=update_data.title
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.delete(
    "/sessions/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a chat session",
)
def delete_chat_session(
    session_id: int = Path(..., description="The ID of the chat session"),
    db: Session = Depends(get_db),
):
    """
    Deletes a chat session and all associated messages.
    """
    success = crud_chat.delete_session(db, session_id=session_id, user_id=APPLICATION_USER_ID)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return None


@router.post(
    "/sessions/{session_id}/messages",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Send message to a specific session",
)
def send_message(
    request: ChatRequest,
    session_id: int = Path(..., description="The ID of the chat session"),
    service: ChatService = Depends(get_chat_service),
    db: Session = Depends(get_db),
) -> ChatResponse:
    """
    Processes a message within an existing context.
    """
    session = crud_chat.get_session(db, session_id=session_id, user_id=APPLICATION_USER_ID)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    response_text, action_taken = service.process_user_message(
        session_id=session_id,
        message=request.message,
        model_preference=request.model_preference,
        model_name=request.model_name,
    )
    return ChatResponse(
        response=response_text,
        session_id=session_id,
        action_taken=action_taken
    )

@router.get(
    "/sessions",
    response_model=List[ChatSessionRead],
    status_code=status.HTTP_200_OK,
    summary="Get paginated chat sessions",
)
def get_chat_sessions(
        skip: int = 0,
        limit: int = Query(default=10, le=100, description="Number of sessions to return (max 100)"),
        db: Session = Depends(get_db),
):
    """
    Retrieves a list of chat sessions for the current user.

    - **skip**: Number of records to skip (for pagination).
    - **limit**: Number of records to return (default 10, max 100).

    Returns the sessions ordered by creation date (newest first).
    """
    sessions = crud_chat.get_user_sessions(
        db, user_id=APPLICATION_USER_ID, skip=skip, limit=limit
    )
    return sessions

@router.get(
    "/sessions/{session_id}/messages",
    response_model=Page[MessageRead],
    status_code=status.HTTP_200_OK,
    summary="Get paginated messages for a session",
)
def get_session_messages(
    session_id: int = Path(..., description="The ID of the chat session"),
    db: Session = Depends(get_db),
):
    """
    Retrieves messages for a specific chat session.
    """
    session = crud_chat.get_session(db, session_id=session_id, user_id=APPLICATION_USER_ID)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    query = crud_chat.get_session_messages(db, session_id)
    return paginate(db, query)