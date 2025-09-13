from pydantic import BaseModel
from typing import Optional

# Shared properties
class IngredientBase(BaseModel):
    name: str
    slug: Optional[str] = None
    description: Optional[str] = None
    cost: Optional[float] = None
    benefits: Optional[str] = None
    claims: Optional[str] = None
    regulatory_notes: Optional[str] = None
    weight: Optional[float] = None
    unit: Optional[str] = None
    allergies: Optional[str] = None
    function: Optional[str] = None
    cost_per_unit: Optional[float] = None

# Properties to receive on item creation
class IngredientCreate(IngredientBase):
    pass

# Properties to receive on item update
class IngredientUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    cost: Optional[float] = None
    benefits: Optional[str] = None
    claims: Optional[str] = None
    regulatory_notes: Optional[str] = None
    weight: Optional[float] = None
    unit: Optional[str] = None
    allergies: Optional[str] = None
    function: Optional[str] = None
    cost_per_unit: Optional[float] = None

# Properties shared by models stored in DB
class IngredientInDBBase(IngredientBase):
    id: int

    class Config:
        from_attributes = True

# Properties to return to client
class Ingredient(IngredientInDBBase):
    pass
