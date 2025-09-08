from sqlalchemy import Column, String, Integer, Float, JSON
from app.core.database import Base

class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True, nullable=False)
    description = Column(String, nullable=True)
    cost = Column(Float, nullable=True)
    vendor = Column(String, nullable=True)
    properties = Column(JSON, nullable=True)
