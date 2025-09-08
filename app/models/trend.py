from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base

class TrendData(Base):
    __tablename__ = "trend_data"

    id = Column(Integer, primary_key=True, index=True)
    source_url = Column(String, nullable=False)
    title = Column(String, nullable=True)
    content = Column(Text, nullable=True)
    category = Column(String, index=True, nullable=True)
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())
