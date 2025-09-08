from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.schemas.ingredient import Ingredient, IngredientCreate
from app.services.ingredient import IngredientService
from app.schemas.utility import APIResponse

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
    return APIResponse(message="Ingredient created successfully", data=ingredient)

@router.get("/", response_model=APIResponse)
def read_ingredients(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = Query(None, description="Search ingredients by name")
):
    """
    Retrieve a list of ingredients with optional search and pagination.
    """
    ingredients = ingredient_service.get_ingredients(db, skip=skip, limit=limit, search=search)
    return APIResponse(message="Ingredients retrieved successfully", data=ingredients)

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
    return APIResponse(message="Ingredient retrieved successfully", data=ingredient)

@router.post("/seed", response_model=APIResponse, status_code=201)
def seed_initial_ingredients(
    db: Session = Depends(get_db)
):
    """
    Seed initial ingredient data into the database.
    """
    created_count = ingredient_service.seed_ingredients(db)
    return APIResponse(message=f"Successfully seeded {created_count} new ingredients.")
