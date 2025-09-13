from pydantic import BaseModel, root_validator
from typing import Optional, List
from app.schemas.ingredient import Ingredient # Import for response model
from app.schemas.supplier import Supplier # Import for response model

# --- Schemas for the relationship ---
class FormulaIngredientBase(BaseModel):
    ingredient_id: int
    quantity: float
    supplier_id: Optional[int] = None # New field

class FormulaIngredientCreate(FormulaIngredientBase):
    pass

class FormulaIngredient(FormulaIngredientBase):
    ingredient: Ingredient
    supplier: Optional[Supplier] = None # New field

    class Config:
        from_attributes = True

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

class FormulaGenerationRequest(BaseModel):
    product_concept: str

# Properties shared by models stored in DB
class FormulaInDBBase(FormulaBase):
    id: int
    author_id: int

    class Config:
        from_attributes = True

# Properties to return to client
class Formula(FormulaInDBBase):
    ingredients: List[FormulaIngredient]
    total_ingredients: int
    total_quantity: float
    total_cost: float
    cost_per_unit: float

    @root_validator(pre=True)
    def calculate_totals(cls, values):
        # When coming from ORM, values is the ORM object itself
        # Create a mutable dictionary from the ORM object
        if hasattr(values, '_sa_instance_state'): # Check if it's an ORM object
            data = values.__dict__.copy()
            # Remove SQLAlchemy internal state
            data.pop('_sa_instance_state', None)
        else:
            data = values.copy() # Assume it's already a dict or similar

        ingredients = data.get("ingredients", [])

        # If ingredients is a list of FormulaIngredient ORM objects, convert them to Pydantic models
        # to access their ingredient details for cost calculation

        data["total_ingredients"] = len(ingredients)
        total_quantity = sum(item.quantity for item in ingredients)
        data["total_quantity"] = total_quantity

        total_cost = 0.0
        for item in ingredients:
            # Check if item is an ORM object and has supplier and price_per_unit
            if hasattr(item, "supplier") and hasattr(item.supplier, "price_per_unit") and item.supplier.price_per_unit is not None:
                total_cost += item.quantity * item.supplier.price_per_unit
            # Check if item is a dictionary and has supplier and price_per_unit
            elif isinstance(item, dict) and "supplier" in item and "price_per_unit" in item["supplier"] and item["supplier"]["price_per_unit"] is not None:
                total_cost += item["quantity"] * item["supplier"]["price_per_unit"]

        data["total_cost"] = total_cost
        data["cost_per_unit"] = total_cost / total_quantity if total_quantity else 0
        return data
