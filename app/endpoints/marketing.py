from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.schemas.utility import APIResponse
from app.schemas.marketing import MarketingCopy
from app.services.marketing import MarketingService
from app.utils.deps import get_current_user

router = APIRouter()

marketing_service = MarketingService()

@router.post("/formulas/{formula_id}/marketing-copy", response_model=APIResponse)
async def generate_marketing_copy(
    formula_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generates marketing copy and a product mockup for a given formula.
    If copy already exists, it will be returned without regeneration.
    """
    copy = await marketing_service.generate_for_formula(db, formula_id)
    return APIResponse(message="Marketing copy generated successfully", data=MarketingCopy.from_orm(copy))

@router.post("/formulas/{formula_id}/regenerate-mockup", response_model=APIResponse)
async def regenerate_mockup(
    formula_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Regenerates the product mockup for a given formula's marketing copy.
    """
    copy = await marketing_service.regenerate_mockup(db, formula_id)
    return APIResponse(message="Product mockup regenerated successfully", data=MarketingCopy.from_orm(copy))
