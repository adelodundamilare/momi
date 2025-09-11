from pydantic import BaseModel, root_validator
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
    product_concept: Optional[str] = None

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
    total_ingredients: int
    total_quantity: float
    total_cost: float
    cost_per_unit: float

    @root_validator(pre=True)
    def calculate_totals(cls, values):
        ingredients = values.get("ingredients", [])
        values["total_ingredients"] = len(ingredients)
        total_quantity = sum(i.quantity for i in ingredients)
        values["total_quantity"] = total_quantity
        total_cost = sum(i.quantity * i.ingredient.cost for i in ingredients if i.ingredient.cost is not None)
        values["total_cost"] = total_cost
        values["cost_per_unit"] = total_cost / total_quantity if total_quantity else 0
        return values
