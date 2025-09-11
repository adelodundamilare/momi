from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.schemas.consumer_insight import ConsumerInsight
from app.services.consumer_insight import ConsumerInsightService
from app.crud.social_post import social_post as social_post_crud
from app.schemas.utility import APIResponse

router = APIRouter()

service = ConsumerInsightService()

def generate_signals_task(db: Session, social_post_ids: List[int]):
    service.generate_trend_signals(db, social_post_ids=social_post_ids)

@router.post("/generate-signals", response_model=APIResponse, status_code=202)
def generate_signals(
    *, 
    db: Session = Depends(get_db), 
    social_post_ids: List[int] = Query(..., description="List of social post IDs to analyze"),
    background_tasks: BackgroundTasks
):
    """
    Initiate trend signal generation from social posts in the background.
    """
    # Basic validation: check if posts exist
    for post_id in social_post_ids:
        if not social_post_crud.get(db, id=post_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Social post with ID {post_id} not found.")

    background_tasks.add_task(generate_signals_task, db, social_post_ids)
    return APIResponse(message="Trend signal generation initiated in the background.")

@router.get("/signals", response_model=APIResponse)
def get_signals(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    insight_type: Optional[str] = Query(None, description="Filter by insight type (e.g., 'trend_signal')")
):
    """
    Retrieve generated consumer insights (trend signals).
    """
    query = db.query(service.crud.model) # Accessing crud model via service for simplicity
    if insight_type:
        query = query.filter(service.crud.model.insight_type == insight_type)
    signals = query.offset(skip).limit(limit).all()
    signals_response = [ConsumerInsight.from_orm(signal) for signal in signals]
    return APIResponse(message="Consumer insights retrieved successfully", data=signals_response)
