from pydantic import BaseModel
from typing import List
from datetime import datetime

class Message(BaseModel):
    role: str # "user", "assistant", or "system"
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    agent_type: str = "innovative" # "innovative" or "compliance"

class ChatHistoryBase(BaseModel):
    user_id: int
    messages: List[Message]

class ChatHistoryCreate(ChatHistoryBase):
    pass

class ChatHistoryUpdate(ChatHistoryBase):
    pass

class ChatHistory(ChatHistoryBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
