from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import datetime
from src.db.models.models import ChatRole


class MessageBase(BaseModel):
    content: str
    role: ChatRole


class MessageCreate(MessageBase):
    meta_data: Optional[Dict[str, Any]] = None


class MessageRead(MessageBase):
    id: int
    created_at: datetime.datetime
    meta_data: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class ChatSessionBase(BaseModel):
    title: Optional[str] = "New Chat"


class ChatSessionInit(BaseModel):
    message: str = Field(
        ..., min_length=1, description="The first message to start the chat."
    )
    model_preference: Optional[str] = Field(
        "dummy", description="local, remote, or dummy"
    )
    model_name: Optional[str] = Field(
        default="gemini-2.5-flash-lite",
        description="The specific model name to use for the LLM.",
    )


class ChatSessionUpdate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)


class ChatSessionRead(ChatSessionBase):
    id: int
    user_id: int
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime]
    messages: List[MessageRead] = []

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="The user's input.")
    model_preference: Optional[str] = Field(
        "dummy", description="local, remote, or dummy"
    )
    model_name: Optional[str] = Field(
        default="gemini-2.5-flash-lite",
        description="The specific model name to use for the LLM.",
    )


class ChatResponse(BaseModel):
    response: str
    session_id: int
    session_title: Optional[str] = (
        None
    )
    action_taken: Optional[str] = None
