from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class SocialPost(Base):
    __tablename__ = "social_posts"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String, nullable=False) # e.g., TikTok, Reddit, Instagram
    author = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    post_date = Column(DateTime(timezone=True), server_default=func.now())
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
