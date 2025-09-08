from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime

# Shared properties
class TrendDataBase(BaseModel):
    source_url: HttpUrl
    category: Optional[str] = None

# Properties to receive on item creation
class TrendDataCreate(TrendDataBase):
    title: str
    content: str

# Schema for initiating a scrape
class ScrapeRequest(BaseModel):
    url: HttpUrl
    category: Optional[str] = None

# Properties shared by models stored in DB
class TrendDataInDBBase(TrendDataBase):
    id: int
    title: Optional[str] = None
    scraped_at: datetime

    class Config:
        orm_mode = True

# Properties to return to client
class TrendData(TrendDataInDBBase):
    pass
