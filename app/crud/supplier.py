from app.crud.base import CRUDBase
from app.models.supplier import Supplier
from app.schemas.supplier import SupplierCreate, SupplierUpdate
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

class CRUDSupplier(CRUDBase[Supplier, SupplierCreate, SupplierUpdate]):
    def create(self, db: Session, *, obj_in: SupplierCreate) -> Supplier:
        obj_in_data = jsonable_encoder(obj_in)
        model_columns = [c.key for c in self.model.__table__.columns]
        filtered_data = {k: v for k, v in obj_in_data.items() if k in model_columns}
        db_obj = self.model(**filtered_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        if hasattr(obj_in, 'ingredient_id') and obj_in.ingredient_id is not None:
            self.link_supplier_to_ingredient(db, db_obj.id, obj_in.ingredient_id)
        return db_obj

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100, search: Optional[str] = None) -> List[Supplier]:
        query = db.query(self.model)
        if search:
            query = query.filter(self.model.full_name.ilike(f"%{search}%"))
        return query.offset(skip).limit(limit).all()

    def get_cheapest_supplier_for_ingredient(self, db: Session, ingredient_id: int) -> Optional[Supplier]:
        from app.models.ingredient import Ingredient # Import here to avoid circular dependency
        return db.query(self.model).join(Ingredient.suppliers).filter(Ingredient.id == ingredient_id).order_by(self.model.price_per_unit.asc()).first()

    def link_supplier_to_ingredient(self, db: Session, supplier_id: int, ingredient_id: int):
        from sqlalchemy import insert
        from app.models.ingredient import ingredient_suppliers
        db.execute(insert(ingredient_suppliers).values(
            ingredient_id=ingredient_id,
            supplier_id=supplier_id
        ))
        db.commit()

supplier = CRUDSupplier(Supplier)
