from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base

class TrendData(Base):
    __tablename__ = "trend_data"

    id = Column(Integer, primary_key=True, index=True)
    link = Column(String, nullable=False)
    title = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    pub_date = Column(DateTime(timezone=True), nullable=True)
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())
    image = Column(String, nullable=True)
    category = Column(String, default='uncategorized', index=True)
    tags = Column(JSON, nullable=True)