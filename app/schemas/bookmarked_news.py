from pydantic import BaseModel

class BookmarkedNewsBase(BaseModel):
    news_feed_id: int

class BookmarkedNewsCreate(BookmarkedNewsBase):
    user_id: int

class BookmarkedNews(BookmarkedNewsBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True
