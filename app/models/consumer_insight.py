from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class ConsumerInsight(Base):
    __tablename__ = "consumer_insights"

    id = Column(Integer, primary_key=True, index=True)
    social_post_id = Column(Integer, ForeignKey("social_posts.id"), nullable=False)
    insight_type = Column(String, nullable=False) # e.g., "trend_signal"
    signal_value = Column(String, nullable=False) # e.g., "Moringa ↑", "Spirulina ↓"
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    model_version = Column(String, nullable=True)
