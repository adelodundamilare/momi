from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.crud.supplier import supplier as supplier_crud
from app.crud.bookmarked_supplier import bookmarked_supplier as bookmarked_supplier_crud
from app.schemas.bookmarked_supplier import BookmarkedSupplierCreate
from app.models.user import User

class SupplierService:
    def get_bookmarked_suppliers(self, *, current_user: User):
        return current_user.bookmarked_suppliers

    def bookmark_supplier(self, *, db: Session, supplier_id: int, current_user: User) -> str:
        db_supplier = supplier_crud.get(db, id=supplier_id)
        if not db_supplier:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found")

        existing_bookmark = bookmarked_supplier_crud.get_by_user_and_supplier(
            db, user_id=current_user.id, supplier_id=supplier_id
        )

        if existing_bookmark:
            bookmarked_supplier_crud.delete(db, id=existing_bookmark.id)
            return "unbookmarked"
        else:
            obj_in = BookmarkedSupplierCreate(user_id=current_user.id, supplier_id=supplier_id)
            bookmarked_supplier_crud.create(db, obj_in=obj_in)
            return "bookmarked"
