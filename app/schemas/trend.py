from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum

class TrendCategory(str, Enum):
    BEVERAGE = "beverage"
    SNACK = "snack"
    PROTEIN = "protein"
    SUPPLEMENT = "supplement"
    UNCATEGORIZED = "uncategorized"

# Shared properties
class TrendDataBase(BaseModel):
    link: HttpUrl
    title: str
    slug: str
    description: Optional[str] = None
    pub_date: Optional[datetime] = None
    image: Optional[str] = None
    category: Optional[TrendCategory] = TrendCategory.UNCATEGORIZED
    tags: Optional[List[str]] = []

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
