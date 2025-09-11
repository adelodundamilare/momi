from sqlalchemy import Column, Integer, ForeignKey
from app.core.database import Base

class BookmarkedNews(Base):
    __tablename__ = "bookmarked_news"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    news_feed_id = Column(Integer, ForeignKey("news_feed.id"), nullable=False)
