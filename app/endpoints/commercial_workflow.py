from fastapi import APIRouter

from app.schemas.commercial_workflow import CommercialWorkflowRequest, CommercialWorkflowResponse
from app.services.commercial_workflow import CommercialWorkflowService
from app.schemas.utility import APIResponse

router = APIRouter()

service = CommercialWorkflowService()

@router.post("/estimate", response_model=APIResponse)
def estimate_commercial_workflow(
    request: CommercialWorkflowRequest
):
    """
    Generates a mock commercialization timeline and suggests co-manufacturers.
    """
    estimate = service.generate_workflow_estimate(request)
    return APIResponse(message="Commercial workflow estimate generated successfully", data=estimate)
