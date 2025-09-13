from app.crud.base import CRUDBase
from app.models.supplier import Supplier
from app.schemas.supplier import SupplierCreate, SupplierUpdate
from typing import List, Optional
from sqlalchemy.orm import Session

class CRUDSupplier(CRUDBase[Supplier, SupplierCreate, SupplierUpdate]):
    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100, search: Optional[str] = None) -> List[Supplier]:
        query = db.query(self.model)
        if search:
            query = query.filter(self.model.full_name.ilike(f"%{search}%"))
        return query.offset(skip).limit(limit).all()

    def get_cheapest_supplier_for_ingredient(self, db: Session, ingredient_id: int) -> Optional[Supplier]:
        from app.models.ingredient import Ingredient # Import here to avoid circular dependency
        return db.query(self.model).join(Ingredient.suppliers).filter(Ingredient.id == ingredient_id).order_by(self.model.price_per_unit.asc()).first()

supplier = CRUDSupplier(Supplier)
