from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class MarketingCopy(Base):
    __tablename__ = "marketing_copies"

    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, index=True)
    tagline = Column(String)
    key_features = Column(JSON)
    marketing_copy = Column(Text)
    product_mockup_url = Column(String, nullable=True)

    formula_id = Column(Integer, ForeignKey("formulas.id"))
    formula = relationship("Formula", back_populates="marketing_copy")
