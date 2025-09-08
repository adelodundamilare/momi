from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SocialPostBase(BaseModel):
    platform: str
    author: str
    content: str
    likes: Optional[int] = 0
    comments: Optional[int] = 0

class SocialPostCreate(SocialPostBase):
    pass

class SocialPostInDBBase(SocialPostBase):
    id: int
    post_date: datetime

    class Config:
        orm_mode = True

class SocialPost(SocialPostInDBBase):
    pass
