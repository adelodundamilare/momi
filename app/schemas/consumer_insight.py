from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ConsumerInsightBase(BaseModel):
    social_post_id: int
    insight_type: str
    signal_value: str
    model_version: Optional[str] = None

class ConsumerInsightCreate(ConsumerInsightBase):
    pass

class ConsumerInsightInDBBase(ConsumerInsightBase):
    id: int
    generated_at: datetime

    class Config:
        orm_mode = True

class ConsumerInsight(ConsumerInsightInDBBase):
    pass
