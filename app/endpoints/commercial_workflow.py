from fastapi import APIRouter

from app.schemas.commercial_workflow import CommercialWorkflowRequest, CommercialWorkflowResponse
from app.services.commercial_workflow import CommercialWorkflowService

router = APIRouter()

service = CommercialWorkflowService()

@router.post("/estimate", response_model=CommercialWorkflowResponse)
def estimate_commercial_workflow(
    request: CommercialWorkflowRequest
):
    """
    Generates a mock commercialization timeline and suggests co-manufacturers.
    """
    estimate = service.generate_workflow_estimate(request)
    return estimate
