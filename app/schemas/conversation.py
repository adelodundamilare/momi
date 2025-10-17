from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.schemas.chat_message import ChatMessage

class ConversationBase(BaseModel):
    title: Optional[str] = None

class ConversationCreate(ConversationBase):
    user_id: int

class ConversationUpdate(ConversationBase):
    pass

class Conversation(ConversationBase):
    id: int
    user_id: int
    created_at: datetime
    messages: List[ChatMessage] = []

    class Config:
        from_attributes = True
