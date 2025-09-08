from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.ingredient import Ingredient, IngredientCreate
from app.services.ingredient import IngredientService

router = APIRouter()

ingredient_service = IngredientService()

@router.post("/", response_model=Ingredient)
def create_ingredient(
    *, 
    db: Session = Depends(get_db), 
    ingredient_in: IngredientCreate
):
    """
    Create new ingredient.
    """
    ingredient = ingredient_service.create_ingredient(db, ingredient_data=ingredient_in)
    return ingredient

@router.get("/{id}", response_model=Ingredient)
def read_ingredient(
    *, 
    db: Session = Depends(get_db), 
    id: int
):
    """
    Get ingredient by ID.
    """
    ingredient = ingredient_service.get_ingredient(db, id=id)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return ingredient
