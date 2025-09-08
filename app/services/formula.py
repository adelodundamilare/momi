from sqlalchemy.orm import Session
from app.crud.formula import formula as formula_crud
from app.crud.ingredient import ingredient as ingredient_crud
from app.schemas.formula import FormulaCreate
from app.models.user import User
from fastapi import HTTPException, status

class FormulaService:
    def create_formula(self, db: Session, *, formula_data: FormulaCreate, current_user: User):
        # Validate that all ingredients exist before creating the formula
        for item in formula_data.ingredients:
            ingredient = ingredient_crud.get(db, id=item.ingredient_id)
            if not ingredient:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Ingredient with id {item.ingredient_id} not found."
                )
        
        return formula_crud.create_with_author(db, obj_in=formula_data, author_id=current_user.id)

    def get_formula(self, db: Session, id: int):
        return formula_crud.get(db, id=id)
