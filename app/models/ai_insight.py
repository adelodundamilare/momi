from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class Insight(Base):
    __tablename__ = "insights"

    id = Column(Integer, primary_key=True, index=True)
    trend_data_id = Column(Integer, ForeignKey("trend_data.id"), nullable=False)
    insight_type = Column(String, nullable=False) # e.g., "summary", "sentiment"
    content = Column(Text, nullable=False)
    model_version = Column(String, nullable=True)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
