from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

from app.crud.base import CRUDBase
from app.models.formula import Formula, FormulaIngredient
from app.schemas.formula import FormulaCreate, FormulaUpdate

class CRUDFormula(CRUDBase[Formula, FormulaCreate, FormulaUpdate]):
    def get(self, db: Session, id: int) -> Optional[Formula]:
        return (
            db.query(self.model)
            .options(joinedload(self.model.ingredients))
            .filter(self.model.id == id)
            .first()
        )

    def get_with_full_details(self, db: Session, id: int) -> Optional[Formula]:
        from app.models.ingredient import Ingredient
        return (
            db.query(self.model)
            .options(
                joinedload(self.model.ingredients).joinedload(FormulaIngredient.ingredient).joinedload(Ingredient.suppliers)
            )
            .filter(self.model.id == id)
            .first()
        )

    def create_with_author(
        self, db: Session, *, obj_in: FormulaCreate, author_id: int
    ) -> Formula:
        formula_data = obj_in.dict(exclude={"ingredients"})
        db_formula = Formula(**formula_data, author_id=author_id)
        db.add(db_formula)
        db.commit()
        db.refresh(db_formula)

        for ingredient_in in obj_in.ingredients:
            db_formula_ingredient = FormulaIngredient(
                formula_id=db_formula.id,
                ingredient_id=ingredient_in.ingredient_id,
                quantity=ingredient_in.quantity,
                supplier_id=ingredient_in.supplier_id,
            )
            db.add(db_formula_ingredient)

        db.commit()
        return self.get(db, id=db_formula.id)

    def get_multi_by_author(self, db: Session, *, author_id: int, skip: int = 0, limit: int = 100) -> List[Formula]:
        return (
            db.query(self.model)
            .options(
                joinedload(self.model.ingredients).joinedload(FormulaIngredient.ingredient),
                joinedload(self.model.ingredients).joinedload(FormulaIngredient.supplier)
            )
            .filter(self.model.author_id == author_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

formula = CRUDFormula(Formula)
