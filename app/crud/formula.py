from sqlalchemy.orm import Session
from typing import List

from app.crud.base import CRUDBase
from app.models.formula import Formula, FormulaIngredient
from app.schemas.formula import FormulaCreate, FormulaUpdate

class CRUDFormula(CRUDBase[Formula, FormulaCreate, FormulaUpdate]):
    def create_with_author(self, db: Session, *, obj_in: FormulaCreate, author_id: int) -> Formula:
        # Create the main Formula object
        formula_data = obj_in.dict(exclude={"ingredients"})
        db_formula = Formula(**formula_data, author_id=author_id)
        db.add(db_formula)
        db.commit()
        db.refresh(db_formula)

        # Create the FormulaIngredient associations
        for ingredient_in in obj_in.ingredients:
            db_formula_ingredient = FormulaIngredient(
                formula_id=db_formula.id,
                ingredient_id=ingredient_in.ingredient_id,
                quantity=ingredient_in.quantity
            )
            db.add(db_formula_ingredient)
        
        db.commit()
        db.refresh(db_formula)
        return db_formula

formula = CRUDFormula(Formula)
