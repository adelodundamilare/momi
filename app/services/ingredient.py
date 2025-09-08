from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.crud.ingredient import ingredient as ingredient_crud
from app.schemas.ingredient import IngredientCreate

class IngredientService:
    def create_ingredient(self, db: Session, *, ingredient_data: IngredientCreate):
        existing_ingredient = ingredient_crud.get_by_name(db, name=ingredient_data.name)
        if existing_ingredient:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"An ingredient with the name '{ingredient_data.name}' already exists."
            )
        return ingredient_crud.create(db, obj_in=ingredient_data)

    def get_ingredient(self, db: Session, id: int):
        return ingredient_crud.get(db, id=id)
