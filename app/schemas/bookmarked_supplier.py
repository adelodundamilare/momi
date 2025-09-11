from pydantic import BaseModel

class BookmarkedSupplierBase(BaseModel):
    user_id: int
    supplier_id: int

class BookmarkedSupplierCreate(BookmarkedSupplierBase):
    pass

class BookmarkedSupplier(BookmarkedSupplierBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True
