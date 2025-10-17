from sqlalchemy.orm import Session
from typing import List, Optional

from app.crud.base import CRUDBase
from app.models.ingredient import Ingredient
from app.schemas.ingredient import IngredientCreate, IngredientUpdate

class CRUDIngredient(CRUDBase[Ingredient, IngredientCreate, IngredientUpdate]):
    def get_by_slug(self, db: Session, *, slug: str) -> Ingredient | None:
        return db.query(self.model).filter(self.model.slug == slug).first()

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100, search: Optional[str] = None) -> List[Ingredient]:
        query = db.query(self.model)
        if search:
            query = query.filter(self.model.name.ilike(f"%{search}%"))
        return query.offset(skip).limit(limit).all()

    def add_supplier(self, db: Session, ingredient: Ingredient, supplier: "Supplier") -> Ingredient:
        if supplier not in ingredient.suppliers:
            ingredient.suppliers.append(supplier)
            db.commit()
            db.refresh(ingredient)
        return ingredient

    def remove_supplier(self, db: Session, ingredient: Ingredient, supplier: "Supplier") -> Ingredient:
        if supplier in ingredient.suppliers:
            ingredient.suppliers.remove(supplier)
            db.commit()
            db.refresh(ingredient)
        return ingredient

ingredient = CRUDIngredient(Ingredient)
