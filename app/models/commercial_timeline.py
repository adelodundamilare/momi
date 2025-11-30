from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class CommercialTimeline(Base):
    __tablename__ = "commercial_timelines"

    id = Column(Integer, primary_key=True, index=True)
    formula_id = Column(Integer, ForeignKey("formulas.id"), nullable=False, index=True)
    timeline_data = Column(JSON, nullable=False)  # Stores AITimelineOutput as JSON
    is_custom = Column(Boolean, default=True)  # True if manually adjusted
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    formula = relationship("Formula", backref="commercial_timelines")
