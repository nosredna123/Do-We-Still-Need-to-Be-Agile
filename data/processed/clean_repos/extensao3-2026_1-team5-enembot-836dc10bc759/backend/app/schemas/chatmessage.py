from pydantic import BaseModel, Field
from typing import Optional

class ChatMessageSchema(BaseModel):
    id: int
    chat_id: int
    author: str = Field(max_length=15)
    texto: str = Field(max_length=15000)
    timestamp: str
    question_id: Optional[int] = None
    essay_id: Optional[int] = None