from pydantic import BaseModel
from typing import Optional, List
from app.schemas.ingredient import Ingredient # Import for response model

# --- Schemas for the relationship ---
class FormulaIngredientBase(BaseModel):
    ingredient_id: int
    quantity: float

class FormulaIngredientCreate(FormulaIngredientBase):
    pass

class FormulaIngredient(FormulaIngredientBase):
    ingredient: Ingredient

    class Config:
        orm_mode = True

# --- Schemas for the main Formula model ---

# Shared properties
class FormulaBase(BaseModel):
    name: str
    description: Optional[str] = None

# Properties to receive on item creation
class FormulaCreate(FormulaBase):
    ingredients: List[FormulaIngredientCreate]

# Properties to receive on item update
class FormulaUpdate(FormulaBase):
    ingredients: Optional[List[FormulaIngredientCreate]] = None

# Properties shared by models stored in DB
class FormulaInDBBase(FormulaBase):
    id: int
    author_id: int

    class Config:
        orm_mode = True

# Properties to return to client
class Formula(FormulaInDBBase):
    ingredients: List[FormulaIngredient]
