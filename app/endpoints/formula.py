from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
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
