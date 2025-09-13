from pydantic import BaseModel
from typing import Optional

class SupplierBase(BaseModel):
    full_name: str
    avatar: Optional[str] = None
    image: Optional[str] = None
    title: Optional[str] = None
    availability: Optional[str] = None
    description: Optional[str] = None
    price_per_unit: Optional[float] = None
    moq_weight_kg: Optional[float] = None
    delivery_duration: Optional[str] = None
    us_approved_status: bool = False

class SupplierCreate(SupplierBase):
    pass

class SupplierUpdate(SupplierBase):
    pass

class SupplierInDBBase(SupplierBase):
    id: int

    class Config:
        from_attributes = True

class Supplier(SupplierInDBBase):
    pass
