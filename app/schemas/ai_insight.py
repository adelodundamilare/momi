from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Shared properties
class InsightBase(BaseModel):
    insight_type: str
    content: str
    model_version: Optional[str] = None

# Properties to receive on item creation
class InsightCreate(InsightBase):
    trend_data_id: int

# Properties shared by models stored in DB
class InsightInDBBase(InsightBase):
    id: int
    trend_data_id: int
    generated_at: datetime

    class Config:
        from_attributes = True

# Properties to return to client
class Insight(InsightInDBBase):
    pass
