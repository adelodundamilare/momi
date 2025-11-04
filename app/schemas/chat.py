from pydantic import BaseModel, Field, validator
from typing import List, Optional

class Message(BaseModel):
    role: str
    content: str = Field(..., min_length=1)

class ChatRequest(BaseModel):
    messages: Optional[List[Message]] = None
    agent_type: str = "innovative"
    conversation_id: int

    @validator('messages')
    def validate_input_method(cls, v, values):
        return v

    class Config:
        extra = "allow"
