from sqlalchemy.orm import Session
from typing import List, Optional

from app.crud.base import CRUDBase
from app.models.ingredient import Ingredient
from app.schemas.ingredient import IngredientCreate, IngredientUpdate

class CRUDIngredient(CRUDBase[Ingredient, IngredientCreate, IngredientUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Ingredient | None:
        return db.query(self.model).filter(self.model.name.ilike(name)).first()

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100, search: Optional[str] = None) -> List[Ingredient]:
        query = db.query(self.model)
        if search:
            query = query.filter(self.model.name.ilike(f"%{search}%"))
        return query.offset(skip).limit(limit).all()

ingredient = CRUDIngredient(Ingredient)
