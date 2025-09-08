from pydantic import BaseModel
from typing import Optional, Any

# Shared properties
class IngredientBase(BaseModel):
    name: str
    description: Optional[str] = None
    cost: Optional[float] = None
    vendor: Optional[str] = None
    properties: Optional[dict[str, Any]] = None

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
