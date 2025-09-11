from sqlalchemy import Column, Integer, String, Float, Boolean, Text
from app.core.database import Base

class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    avatar = Column(String, nullable=True)
    image = Column(String, nullable=True)
    title = Column(String, nullable=True)
    availability = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    price_per_kg = Column(Float, nullable=True)
    moq_weight_kg = Column(Float, nullable=True)
    delivery_duration = Column(String, nullable=True)
    us_approved_status = Column(Boolean, default=False)
