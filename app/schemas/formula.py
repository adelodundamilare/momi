from pydantic import BaseModel, root_validator
from typing import Optional, List
from datetime import datetime
from app.schemas.ingredient import Ingredient
from app.schemas.supplier import Supplier

class FormulaIngredientBase(BaseModel):
    ingredient_id: int
    quantity: float
    supplier_id: Optional[int] = None

class FormulaIngredientCreate(FormulaIngredientBase):
    pass

class FormulaIngredient(FormulaIngredientBase):
    ingredient: Ingredient
    supplier: Optional[Supplier] = None

    class Config:
        from_attributes = True

class FormulaBase(BaseModel):
    name: str
    description: Optional[str] = None
    product_concept: Optional[str] = None


class FormulaCreate(FormulaBase):
    ingredients: List[FormulaIngredientCreate]

class FormulaUpdate(FormulaBase):
    ingredients: Optional[List[FormulaIngredientCreate]] = None

class FormulaGenerationRequest(BaseModel):
    product_concept: str
    market_insights: Optional[dict] = None

class FormulaInDBBase(FormulaBase):
    id: int
    author_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Formula(FormulaInDBBase):
    ingredients: List[FormulaIngredient]
    total_ingredients: int
    total_quantity: float
    total_cost: float
    cost_per_unit: float

    @root_validator(pre=True)
    def calculate_totals(cls, values):
        if hasattr(values, '_sa_instance_state'):
            data = values.__dict__.copy()
            data.pop('_sa_instance_state', None)
        else:
            data = values.copy()

        ingredients = data.get("ingredients", [])

        data["total_ingredients"] = len(ingredients)
        total_quantity = sum(item.quantity for item in ingredients)
        data["total_quantity"] = total_quantity

        total_cost = 0.0
        for item in ingredients:
            if hasattr(item, "supplier") and hasattr(item.supplier, "price_per_unit") and item.supplier.price_per_unit is not None:
                total_cost += item.quantity * item.supplier.price_per_unit
            elif isinstance(item, dict) and "supplier" in item and "price_per_unit" in item["supplier"] and item["supplier"]["price_per_unit"] is not None:
                total_cost += item["quantity"] * item["supplier"]["price_per_unit"]

        data["total_cost"] = total_cost
        data["cost_per_unit"] = total_cost / total_quantity if total_quantity else 0
        return data
