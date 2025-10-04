from pydantic import BaseModel, validator, Field
from typing import List
from datetime import datetime

class Message(BaseModel):
    role: str
    content: str = Field(..., min_length=1)

class ChatRequest(BaseModel):
    messages: List[Message] = Field(..., min_length=1)
    agent_type: str = "innovative"

    @validator('messages')
    def last_message_must_be_from_user(cls, v):
        if v and v[-1].role != 'user':
            raise ValueError('The last message must be from the "user"')
        return v

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
