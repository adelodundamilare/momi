from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Union

from app.core.database import get_db
from app.schemas.ingredient import Ingredient, IngredientCreate
from app.models.ingredient import Ingredient as IngredientModel
from app.services.ingredient import IngredientService
from app.schemas.utility import APIResponse

from app.models.trend import TrendData
from app.schemas.ingredient_price_chart import IngredientPriceChart, PricePoint
from datetime import date, timedelta
import random

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

@router.get("/{slug}/price-chart", response_model=APIResponse)
def get_ingredient_price_chart(
    slug: str,
    db: Session = Depends(get_db),
    days: int = Query(30, ge=7, le=365, description="Number of days for price history")
):
    """
    Generates random price movement data for an ingredient for charting.
    """
    ingredient = ingredient_service.get_by_slug(db, slug=slug)

    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    base_price = ingredient.cost if ingredient.cost is not None else 10.0 # Default if cost is null
    chart_data = []
    current_date = date.today()

    for i in range(days):
        day_date = current_date - timedelta(days=days - 1 - i)
        # Simulate price movement: +/- 5% of base price, with some randomness
        price_change = (random.random() - 0.5) * 0.1 * base_price # +/- 5% of base
        price = max(0.1, base_price + price_change) # Ensure price doesn't go below 0.1
        chart_data.append(PricePoint(date=day_date, price=round(price, 2)))

    return APIResponse(
        message="Ingredient price chart data generated successfully",
        data=IngredientPriceChart(
            ingredient_id=ingredient.id,
            ingredient_name=ingredient.name,
            chart_data=chart_data
        )
    )


