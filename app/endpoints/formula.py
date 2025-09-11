from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.core.database import get_db
from app.schemas.formula import Formula, FormulaCreate
from app.services.formula import FormulaService
from app.utils.deps import get_current_user
from app.models.user import User
from app.schemas.utility import APIResponse

from app.schemas.formula_analysis import FormulaAnalysis

router = APIRouter()

formula_service = FormulaService()

@router.post("/", response_model=APIResponse)
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
    formula_response = Formula.from_orm(formula)
    return APIResponse(message="Formula created successfully", data=formula_response)

@router.get("/{id}", response_model=APIResponse)
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
    formula_response = Formula.from_orm(formula)
    return APIResponse(message="Formula retrieved successfully", data=formula_response)

@router.get("/suggest-substitutions", response_model=APIResponse)
def suggest_substitutions(
    ingredient_name: str = Query(..., description="Name of the ingredient to find substitutions for")
):
    """
    Suggests alternative ingredients using AI.
    """
    suggestions = formula_service.suggest_ingredient_substitutions(ingredient_name)
    return APIResponse(message="Ingredient substitutions suggested", data=suggestions)

@router.get("/{formula_id}/nutrition-panel", response_model=APIResponse)
def get_nutrition_panel(
    formula_id: int
):
    """
    Generates a mock Nutrition Facts Panel for a given formula.
    (No real calculations at MVP stage).
    """
    nutrition_panel = formula_service.generate_mock_nutrition_panel(formula_id)
    return APIResponse(message="Mock nutrition panel generated", data=nutrition_panel)

@router.get("/{formula_id}/analysis", response_model=APIResponse)
def get_formula_analysis(
    formula_id: int
):
    """
    Get AI analysis for a formula.
    """
    mock_data = {
        "estimated_cost_per_unit": 1.25,
        "batch_cost": 1250.0,
        "savings_percentage": 15.0,
        "allergy_alerts": ["Contains nuts"],
        "sustainability_score": 8.5,
        "suggestions": ["Replace sugar with stevia to reduce cost", "Source ingredients locally to improve sustainability"],
    }
    return APIResponse(message="Formula analysis retrieved successfully", data=mock_data)

@router.get("/{formula_id}/export/excel", response_model=APIResponse)
def export_formula_excel(
    formula_id: int
):
    """
    Export formula to Excel.
    """
    return APIResponse(message="Excel export is not implemented yet.")

@router.get("/{formula_id}/export/pdf", response_model=APIResponse)
def export_formula_pdf(
    formula_id: int
):
    """
    Export formula to PDF.
    """
    return APIResponse(message="PDF export is not implemented yet.")
