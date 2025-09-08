from pydantic import BaseModel
from typing import Optional

# Shared properties
class IngredientBase(BaseModel):
    name: str
    description: Optional[str] = None
    cost: Optional[float] = None
    vendor: Optional[str] = None
    benefits: Optional[str] = None
    claims: Optional[str] = None
    regulatory_notes: Optional[str] = None

# Properties to receive on item creation
class IngredientCreate(IngredientBase):
    pass

# Properties to receive on item update
class IngredientUpdate(IngredientBase):
    pass

# Properties shared by models stored in DB
class IngredientInDBBase(IngredientBase):
    id: int

    class Config:
        orm_mode = True

# Properties to return to client
class Ingredient(IngredientInDBBase):
    pass
