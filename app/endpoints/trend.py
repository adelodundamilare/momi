from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.trend import TrendData, ScrapeRequest
from app.services.trend import TrendService
from app.schemas.utility import APIResponse
from app.utils.logger import setup_logger

logger = setup_logger("trend_api", "trend.log")

router = APIRouter()

trend_service = TrendService()

def scrape_task(db: Session, url: str, category: str | None, tags: List[str] | None):
    trend_service.scrape_and_save(db, url=url, category=category, tags=tags)

@router.post("/scrape", response_model=APIResponse)
def scrape_url(
    *, 
    db: Session = Depends(get_db), 
    request: ScrapeRequest,
    background_tasks: BackgroundTasks
):
    """
    Initiate scraping of a URL in the background.
    """
    try:
        background_tasks.add_task(scrape_task, db, str(request.url), request.category, request.tags)
        return APIResponse(message="Scraping has been initiated in the background.")
    except Exception as e:
        logger.error(f"Error in scrape_url: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/", response_model=APIResponse)
def read_trends(
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of scraped trends.
    """
    try:
        trends = trend_service.get_trends(db)
        trends_response = [TrendData.from_orm(trend) for trend in trends]
        return APIResponse(message="Scraped trends retrieved successfully", data=trends_response)
    except Exception as e:
        logger.error(f"Error in read_trends: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
