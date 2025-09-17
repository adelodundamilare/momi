from pydantic import BaseModel, HttpUrl, computed_field
from typing import Optional
from datetime import datetime
import random

class NewsFeedBase(BaseModel):
    title: str
    slug: str
    source: str
    url: HttpUrl
    image: Optional[str] = None
    published_at: Optional[datetime] = None

class NewsFeedCreate(NewsFeedBase):
    pass

class NewsFeedUpdate(NewsFeedBase):
    pass

class NewsFeedInDBBase(NewsFeedBase):
    id: int

    class Config:
        from_attributes = True

class NewsFeed(NewsFeedInDBBase):
    @computed_field
    @property
    def views(self) -> int:
        return random.randint(100, 10000)
