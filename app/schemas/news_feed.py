from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime
import random

class NewsFeedBase(BaseModel):
    title: str
    source: str
    url: HttpUrl
    image: Optional[str] = None
    views: int = random.randint(100, 10000)

class NewsFeedCreate(NewsFeedBase):
    pass

class NewsFeedUpdate(NewsFeedBase):
    pass

class NewsFeedInDBBase(NewsFeedBase):
    id: int
    published_at: datetime

    class Config:
        from_attributes = True

class NewsFeed(NewsFeedInDBBase):
    pass
