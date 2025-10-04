from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

# Association Table for the many-to-many relationship
class FormulaIngredient(Base):
    __tablename__ = 'formula_ingredients'
    formula_id = Column(Integer, ForeignKey('formulas.id'), primary_key=True)
    ingredient_id = Column(Integer, ForeignKey('ingredients.id'), primary_key=True)
    supplier_id = Column(Integer, ForeignKey('suppliers.id'), nullable=True)
    quantity = Column(Float, nullable=False)

    ingredient = relationship("Ingredient")
    supplier = relationship("Supplier")

class Formula(Base):
    __tablename__ = "formulas"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    product_concept = Column(String, nullable=True)
    author_id = Column(Integer, ForeignKey("users.id"))

    author = relationship("User")
    ingredients = relationship("FormulaIngredient")
    marketing_copy = relationship("MarketingCopy", back_populates="formula", uselist=False)
