from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.commercial_workflow import CommercialWorkflowService
from app.schemas.commercial_workflow_analysis import CommercializationAnalysisOutput
from app.schemas.utility import APIResponse
from app.utils.logger import setup_logger

logger = setup_logger("commercial_workflow_api", "commercial_workflow.log")

router = APIRouter()
service = CommercialWorkflowService()

@router.get("/formulas/{formula_id}/analyze", response_model=APIResponse[CommercializationAnalysisOutput])
async def analyze_formula_workflow(
    formula_id: int,
    db: Session = Depends(get_db)
):
    """
    Analyzes a formula to generate a commercialization workflow, including
    timelines, risk analysis, and recommendations.
    """
    try:
        analysis = await service.analyze_formula(db=db, formula_id=formula_id)
        return APIResponse(message="Commercialization analysis generated successfully", data=analysis)
    except Exception as e:
        logger.error(f"Error in analyze_formula_workflow: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))