from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional, Union

from app.core.database import get_db
from app.schemas.ingredient import Ingredient, IngredientCreate
from app.models.ingredient import Ingredient as IngredientModel
from app.services.ingredient import IngredientService
from app.services.ai_provider import OpenAIProvider
from app.schemas.utility import APIResponse

from app.models.trend import TrendData
from app.schemas.ingredient_price_chart import IngredientPriceChart, PricePoint
from datetime import date, timedelta
import random
from app.utils.logger import setup_logger

logger = setup_logger("ingredient_api", "ingredient.log")

router = APIRouter()

ingredient_service = IngredientService(ai_provider=OpenAIProvider())

@router.post("/", response_model=APIResponse)
def create_ingredient(
    *,
    db: Session = Depends(get_db),
    ingredient_in: IngredientCreate
):
    """
    Create new ingredient.
    """
    try:
        ingredient = ingredient_service.create_ingredient(db, ingredient_data=ingredient_in)
        ingredient_response = Ingredient.from_orm(ingredient)
        return APIResponse(message="Ingredient created successfully", data=ingredient_response)
    except Exception as e:
        logger.error(f"Error in create_ingredient: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

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
    try:
        query = db.query(IngredientModel)
        if search:
            query = query.filter(IngredientModel.name.ilike(f"%{search}%"))
        if trending:
            query = query.join(TrendData, TrendData.content.contains(IngredientModel.name))
        if type:
            query = query.filter(IngredientModel.function.ilike(type))
        ingredients = query.offset(skip).limit(limit).all()
        ingredients_response = [Ingredient.from_orm(ingredient) for ingredient in ingredients]
        return APIResponse(message="Ingredients retrieved successfully", data=ingredients_response)
    except Exception as e:
        logger.error(f"Error in read_ingredients: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{slug}/price-chart", response_model=APIResponse)
def get_ingredient_price_chart(
    slug: str,
    db: Session = Depends(get_db),
    days: int = Query(30, ge=7, le=365, description="Number of days for price history")
):
    """
    Generates random price movement data for an ingredient for charting.
    """
    try:
        ingredient = ingredient_service.get_by_slug(db, slug=slug)

        if not ingredient:
            raise HTTPException(status_code=404, detail="Ingredient not found")

        # Get base price from an associated supplier
        base_price = None
        if ingredient.suppliers:
            # For simplicity, use the price from the first supplier
            base_price = ingredient.suppliers[0].price_per_unit

        if base_price is None:
            raise HTTPException(status_code=404, detail="Ingredient has no associated suppliers with price data.")

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
    except Exception as e:
        logger.error(f"Error in get_ingredient_price_chart: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/{ingredient_id}/suppliers/{supplier_id}", response_model=APIResponse)
def add_supplier_to_ingredient(
    ingredient_id: int,
    supplier_id: int,
    db: Session = Depends(get_db)
):
    """
    Associate a supplier with an ingredient.
    """
    try:
        ingredient = ingredient_service.add_supplier_to_ingredient(db, ingredient_id, supplier_id)
        return APIResponse(message="Supplier associated with ingredient successfully", data=Ingredient.from_orm(ingredient))
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error in add_supplier_to_ingredient: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/{ingredient_id}/suppliers/{supplier_id}", response_model=APIResponse)
def remove_supplier_from_ingredient(
    ingredient_id: int,
    supplier_id: int,
    db: Session = Depends(get_db)
):
    """
    Disassociate a supplier from an ingredient.
    """
    try:
        ingredient = ingredient_service.remove_supplier_from_ingredient(db, ingredient_id, supplier_id)
        return APIResponse(message="Supplier disassociated from ingredient successfully", data=Ingredient.from_orm(ingredient))
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error in remove_supplier_from_ingredient: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

