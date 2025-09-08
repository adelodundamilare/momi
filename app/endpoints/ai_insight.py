from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.ai_insight import Insight
from app.services.ai_insight import AIInsightService
from app.crud.trend import trend as trend_crud

router = APIRouter()

insight_service = AIInsightService()

def insight_task(db: Session, trend_id: int):
    insight_service.generate_and_save_insights(db, trend_id=trend_id)

@router.post("/generate/{trend_id}")
def generate_insights(
    *, 
    db: Session = Depends(get_db), 
    trend_id: int,
    background_tasks: BackgroundTasks
):
    """
    Initiate AI insight generation for a trend in the background.
    """
    trend = trend_crud.get(db, id=trend_id)
    if not trend:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trend not found")

    background_tasks.add_task(insight_task, db, trend_id)
    return {"message": "AI insight generation has been initiated in the background."}

@router.get("/trend/{trend_id}", response_model=List[Insight])
def read_insights_for_trend(
    *, 
    db: Session = Depends(get_db), 
    trend_id: int
):
    """
    Retrieve all insights for a specific trend.
    """
    # A more specific CRUD method could be created for this, but for now a simple query suffices.
    insights = db.query(insight_crud.model).filter(insight_crud.model.trend_data_id == trend_id).all()
    return insights
