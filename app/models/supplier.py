from sqlalchemy import Column, Integer, String, Float, Boolean, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.ingredient import ingredient_suppliers

class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    avatar = Column(String, nullable=True)
    image = Column(String, nullable=True)
    title = Column(String, nullable=True)
    availability = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    price_per_unit = Column(Float, nullable=True)
    moq_weight_kg = Column(Float, nullable=True)
    delivery_duration = Column(String, nullable=True)
    us_approved_status = Column(Boolean, default=False)

    ingredients = relationship("Ingredient", secondary=ingredient_suppliers, back_populates="suppliers")
    bookmarked_by = relationship("BookmarkedSupplier", back_populates="supplier", cascade="all, delete-orphan")
