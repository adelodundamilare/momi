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
    nutritional_facts = Column(JSON, nullable=True)
    estimated_cost_per_unit = Column(JSON, nullable=True)
    batch_cost = Column(JSON, nullable=True)
    potential_savings = Column(JSON, nullable=True)
    suggestions = Column(JSON, nullable=True)
    allergen_alerts = Column(JSON, nullable=True)
    sustainability = Column(JSON, nullable=True)
    calories = Column(Integer, nullable=True)
    serving_size_per_bottle = Column(String, nullable=True)
    suppliers_index = Column(JSON, nullable=True)

    formula_id = Column(Integer, ForeignKey("formulas.id"))
    formula = relationship("Formula", back_populates="marketing_copy")
