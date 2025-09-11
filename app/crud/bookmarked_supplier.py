from app.crud.base import CRUDBase
from app.models.bookmarked_supplier import BookmarkedSupplier
from app.schemas.bookmarked_supplier import BookmarkedSupplierCreate

class CRUDBookmarkedSupplier(CRUDBase[BookmarkedSupplier, BookmarkedSupplierCreate, None]):
    pass

bookmarked_supplier = CRUDBookmarkedSupplier(BookmarkedSupplier)
