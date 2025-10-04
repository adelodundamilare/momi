from typing import Optional
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.bookmarked_supplier import BookmarkedSupplier
from app.schemas.bookmarked_supplier import BookmarkedSupplierCreate

class CRUDBookmarkedSupplier(CRUDBase[BookmarkedSupplier, BookmarkedSupplierCreate, None]):
    def get_by_user_and_supplier(self, db: Session, *, user_id: int, supplier_id: int) -> Optional[BookmarkedSupplier]:
        return db.query(self.model).filter(
            self.model.user_id == user_id, 
            self.model.supplier_id == supplier_id
        ).first()

bookmarked_supplier = CRUDBookmarkedSupplier(BookmarkedSupplier)
