from fastapi import APIRouter, HTTPException, status

from app.schemas.commercial_workflow import CommercialWorkflowRequest, CommercialWorkflowResponse
from app.services.commercial_workflow import CommercialWorkflowService
from app.schemas.utility import APIResponse
from app.utils.logger import setup_logger

logger = setup_logger("commercial_workflow_api", "commercial_workflow.log")

router = APIRouter()

service = CommercialWorkflowService()

@router.post("/estimate", response_model=APIResponse)
def estimate_commercial_workflow(
    request: CommercialWorkflowRequest
):
    """
    Generates a mock commercialization timeline and suggests co-manufacturers.
    """
    try:
        estimate = service.generate_workflow_estimate(request)
        return APIResponse(message="Commercial workflow estimate generated successfully", data=estimate)
    except Exception as e:
        logger.error(f"Error in estimate_commercial_workflow: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
