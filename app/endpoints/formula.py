from fastapi import APIRouter, Depends, HTTPException, Query, status, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.schemas.formula import Formula, FormulaGenerationRequest
from app.schemas.utility import APIResponse
from app.services.formula import FormulaService
from app.utils.deps import get_current_user

router = APIRouter()

formula_service = FormulaService()


@router.get("/{id}", response_model=APIResponse)
def read_formula(*, db: Session = Depends(get_db), id: int):
    """
    Get formula by ID.
    """
    formula = formula_service.get_formula(db, id=id)
    if not formula:
        raise HTTPException(status_code=404, detail="Formula not found")
    formula_response = Formula.from_orm(formula)
    return APIResponse(message="Formula retrieved successfully", data=formula_response)


@router.post("/generate-from-concept", response_model=APIResponse)
def generate_formula_from_concept(
    request: FormulaGenerationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generates a formula based on a product concept using AI.
    """
    generated_formula_data = formula_service.generate_formula_from_concept(
        db, request.product_concept, current_user, background_tasks
    )
    formula_response = Formula.from_orm(generated_formula_data)
    return APIResponse(message="Formula generated successfully", data=formula_response)


@router.get("/suggest-substitutions", response_model=APIResponse)
def suggest_substitutions(
    ingredient_name: str = Query(
        ..., description="Name of the ingredient to find substitutions for"
    )
):
    """
    Suggests alternative ingredients using AI.
    """
    suggestions = formula_service.suggest_ingredient_substitutions(ingredient_name)
    return APIResponse(message="Ingredient substitutions suggested", data=suggestions)


@router.get("/{formula_id}/export/excel")
def export_formula_excel(
    formula_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Export formula to Excel.
    """
    excel_file = formula_service.export_formula_excel(db, formula_id)
    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=formula_{formula_id}.xlsx"},
    )


@router.get("/{formula_id}/export/pdf")
def export_formula_pdf(
    formula_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Export formula to PDF.
    """
    pdf_file = formula_service.export_formula_pdf(db, formula_id)
    return StreamingResponse(
        pdf_file,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=formula_{formula_id}.pdf"},
    )