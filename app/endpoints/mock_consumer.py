from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.mock_consumer import MockConsumer
from app.services.mock_consumer import MockConsumerService
from app.schemas.utility import APIResponse

router = APIRouter()

service = MockConsumerService()

@router.post("/generate", response_model=APIResponse, status_code=201)
def generate_mock_consumers(
    *, 
    db: Session = Depends(get_db),
    count: int = Query(10, ge=1, le=100, description="Number of consumers to generate (1-100)")
):
    """
    Generate a specified number of mock consumers and save them to the database.
    """
    generated = service.generate_consumers(db, count=count)
    return APIResponse(message=f"Successfully generated {len(generated)} mock consumers.")

@router.get("/", response_model=APIResponse)
def read_mock_consumers(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    Retrieve a list of mock consumers with pagination.
    """
    consumers = service.get_consumers(db, skip=skip, limit=limit)
    consumers_response = [MockConsumer.from_orm(consumer) for consumer in consumers]
    return APIResponse(message="Mock consumers retrieved successfully", data=consumers_response)
