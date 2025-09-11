from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.schemas.ingredient import Ingredient, IngredientCreate
from app.models.ingredient import Ingredient as IngredientModel
from app.services.ingredient import IngredientService
from app.schemas.utility import APIResponse

from app.models.trend import TrendData

router = APIRouter()

ingredient_service = IngredientService()

@router.post("/", response_model=APIResponse)
def create_ingredient(
    *, 
    db: Session = Depends(get_db), 
    ingredient_in: IngredientCreate
):
    """
    Create new ingredient.
    """
    ingredient = ingredient_service.create_ingredient(db, ingredient_data=ingredient_in)
    ingredient_response = Ingredient.from_orm(ingredient)
    return APIResponse(message="Ingredient created successfully", data=ingredient_response)

@router.get("/", response_model=APIResponse)
def read_ingredients(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = Query(None, description="Search ingredients by name"),
    trending: Optional[bool] = Query(None, description="Filter by trending ingredients"),
    type: Optional[str] = Query(None, description="Filter by ingredient type (function)")
):
    """
    Retrieve a list of ingredients with optional search and pagination.
    """
    query = db.query(IngredientModel)
    if search:
        query = query.filter(IngredientModel.name.contains(search))
    if trending:
        query = query.join(TrendData, TrendData.content.contains(IngredientModel.name))
    if type:
        query = query.filter(IngredientModel.function == type)
    ingredients = query.offset(skip).limit(limit).all()
    ingredients_response = [Ingredient.from_orm(ingredient) for ingredient in ingredients]
    return APIResponse(message="Ingredients retrieved successfully", data=ingredients_response)

@router.get("/{id}", response_model=APIResponse)
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
    ingredient_response = Ingredient.from_orm(ingredient)
    return APIResponse(message="Ingredient retrieved successfully", data=ingredient_response)


