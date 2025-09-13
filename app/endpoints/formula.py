from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.core.database import get_db
from app.schemas.formula import Formula

from app.utils.deps import get_current_user
from app.models.user import User
from app.schemas.utility import APIResponse

from app.schemas.formula_analysis import FormulaAnalysis

from app.schemas.formula import FormulaGenerationRequest
from app.services.formula import FormulaService
from app.utils.logger import setup_logger

logger = setup_logger("formula_api", "formula.log")


router = APIRouter()

formula_service = FormulaService()



@router.get("/{id}", response_model=APIResponse)
def read_formula(
    *,
    db: Session = Depends(get_db),
    id: int
):
    """
    Get formula by ID.
    """
    try:
        formula = formula_service.get_formula(db, id=id)
        if not formula:
            raise HTTPException(status_code=404, detail="Formula not found")
        formula_response = Formula.from_orm(formula)
        return APIResponse(message="Formula retrieved successfully", data=formula_response)
    except Exception as e:
        logger.error(f"Error in read_formula: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/generate-from-concept", response_model=APIResponse)
def generate_formula_from_concept(
    request: FormulaGenerationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generates a formula based on a product concept using AI.
    """
    try:
        generated_formula_data = formula_service.generate_formula_from_concept(db, request.product_concept, current_user)
        formula_response = Formula.from_orm(generated_formula_data)
        return APIResponse(message="Formula generated successfully", data=formula_response)
    except Exception as e:
        logger.error(f"Error in generate_formula_from_concept: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/suggest-substitutions", response_model=APIResponse)
def suggest_substitutions(
    ingredient_name: str = Query(..., description="Name of the ingredient to find substitutions for")
):
    """
    Suggests alternative ingredients using AI.
    """
    try:
        suggestions = formula_service.suggest_ingredient_substitutions(ingredient_name)
        return APIResponse(message="Ingredient substitutions suggested", data=suggestions)
    except Exception as e:
        logger.error(f"Error in suggest_substitutions: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{formula_id}/nutrition-panel", response_model=APIResponse)
def get_nutrition_panel(
    formula_id: int
):
    """
    Generates a mock Nutrition Facts Panel for a given formula.
    (No real calculations at MVP stage).
    """
    try:
        nutrition_panel = formula_service.generate_mock_nutrition_panel(formula_id)
        return APIResponse(message="Mock nutrition panel generated", data=nutrition_panel)
    except Exception as e:
        logger.error(f"Error in get_nutrition_panel: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{formula_id}/analysis", response_model=APIResponse)
def get_formula_analysis(
    formula_id: int
):
    """
    Get AI analysis for a formula.
    """
    try:
        mock_data = {
            "estimated_cost_per_unit": 1.25,
            "batch_cost": 1250.0,
            "savings_percentage": 15.0,
            "allergy_alerts": ["Contains nuts"],
            "sustainability_score": 8.5,
            "suggestions": ["Replace sugar with stevia to reduce cost", "Source ingredients locally to improve sustainability"],
        }
        return APIResponse(message="Formula analysis retrieved successfully", data=mock_data)
    except Exception as e:
        logger.error(f"Error in get_formula_analysis: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{formula_id}/export/excel", response_model=APIResponse)
def export_formula_excel(
    formula_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Export formula to Excel.
    """
    try:
        return APIResponse(message="Excel export is not implemented yet.")
    except Exception as e:
        logger.error(f"Error in export_formula_excel: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{formula_id}/export/pdf", response_model=APIResponse)
def export_formula_pdf(
    formula_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Export formula to PDF.
    """
    try:
        return APIResponse(message="PDF export is not implemented yet.")
    except Exception as e:
        logger.error(f"Error in export_formula_pdf: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
