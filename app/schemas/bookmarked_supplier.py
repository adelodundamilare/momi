from pydantic import BaseModel

class BookmarkedSupplierBase(BaseModel):
    supplier_id: int

class BookmarkedSupplierCreate(BookmarkedSupplierBase):
    pass

class BookmarkedSupplier(BookmarkedSupplierBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True
