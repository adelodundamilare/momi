from sqlalchemy import Column, String, Integer, Float, Text, Table, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

# Association Table for Many-to-Many relationship between Ingredient and Supplier
ingredient_suppliers = Table(
    'ingredient_suppliers',
    Base.metadata,
    Column('ingredient_id', Integer, ForeignKey('ingredients.id'), primary_key=True),
    Column('supplier_id', Integer, ForeignKey('suppliers.id'), primary_key=True)
)

class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    cost = Column(Float, nullable=True)
    benefits = Column(Text, nullable=True)
    claims = Column(Text, nullable=True)
    regulatory_notes = Column(Text, nullable=True)
    weight = Column(Float, nullable=True)
    unit = Column(String, nullable=True)
    allergies = Column(String, nullable=True)
    function = Column(String, nullable=True)
    cost_per_unit = Column(Float, nullable=True)

    suppliers = relationship("Supplier", secondary=ingredient_suppliers, back_populates="ingredients")
