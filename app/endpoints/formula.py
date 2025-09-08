from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.core.database import get_db
from app.schemas.formula import Formula, FormulaCreate
from app.services.formula import FormulaService
from app.utils.deps import get_current_user
from app.models.user import User

router = APIRouter()

formula_service = FormulaService()

@router.post("/", response_model=Formula)
def create_formula(
    *, 
    db: Session = Depends(get_db), 
    formula_in: FormulaCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create new formula. Requires authentication.
    """
    formula = formula_service.create_formula(db, formula_data=formula_in, current_user=current_user)
    return formula

@router.get("/{id}", response_model=Formula)
def read_formula(
    *, 
    db: Session = Depends(get_db), 
    id: int
):
    """
    Get formula by ID.
    """
    formula = formula_service.get_formula(db, id=id)
    if not formula:
        raise HTTPException(status_code=404, detail="Formula not found")
    return formula

@router.get("/suggest-substitutions", response_model=List[str])
def suggest_substitutions(
    ingredient_name: str = Query(..., description="Name of the ingredient to find substitutions for")
):
    """
    Suggests alternative ingredients using AI.
    """
    suggestions = formula_service.suggest_ingredient_substitutions(ingredient_name)
    return suggestions

@router.get("/{formula_id}/nutrition-panel", response_model=Dict[str, Any])
def get_nutrition_panel(
    formula_id: int
):
    """
    Generates a mock Nutrition Facts Panel for a given formula.
    (No real calculations at MVP stage).
    """
    nutrition_panel = formula_service.generate_mock_nutrition_panel(formula_id)
    return nutrition_panel
