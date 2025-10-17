from pydantic import BaseModel
from datetime import datetime

class ChatMessageBase(BaseModel):
    role: str
    content: str
    conversation_id: int

class ChatMessageCreate(ChatMessageBase):
    pass

class ChatMessageUpdate(ChatMessageBase):
    pass

class ChatMessage(ChatMessageBase):
    id: int
    conversation_id: int
    created_at: datetime

    class Config:
        from_attributes = True
