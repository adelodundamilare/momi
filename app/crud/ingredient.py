from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.ingredient import Ingredient
from app.schemas.ingredient import IngredientCreate, IngredientUpdate

class CRUDIngredient(CRUDBase[Ingredient, IngredientCreate, IngredientUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Ingredient | None:
        return db.query(self.model).filter(self.model.name.ilike(name)).first()

ingredient = CRUDIngredient(Ingredient)
