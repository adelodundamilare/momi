from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List, Dict
from datetime import datetime

# Shared properties
class TrendDataBase(BaseModel):
    link: HttpUrl
    title: str
    slug: str # Added slug field
    description: Optional[str] = None
    pub_date: Optional[datetime] = None
    image: Optional[str] = None

# Properties to receive on item creation
class TrendDataCreate(TrendDataBase):
    pass

# Schema for initiating a scrape
class ScrapeRequest(BaseModel):
    url: HttpUrl
    category: Optional[str] = None
    tags: Optional[List[str]] = None

# Properties shared by models stored in DB
class TrendDataInDBBase(TrendDataBase):
    id: int
    scraped_at: datetime

    class Config:
        from_attributes = True

# Properties to return to client
class TrendData(TrendDataInDBBase):
    pass
