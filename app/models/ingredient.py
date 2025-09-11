from sqlalchemy import Column, String, Integer, Float, Text
from app.core.database import Base

class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    cost = Column(Float, nullable=True)
    vendor = Column(String, nullable=True)
    benefits = Column(Text, nullable=True)
    claims = Column(Text, nullable=True)
    regulatory_notes = Column(Text, nullable=True)
    weight = Column(Float, nullable=True)
    unit = Column(String, nullable=True)
    allergies = Column(String, nullable=True)
    function = Column(String, nullable=True)
    cost_per_unit = Column(Float, nullable=True)
