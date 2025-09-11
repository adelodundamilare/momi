from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.trend import TrendData, ScrapeRequest
from app.services.trend import TrendService
from app.schemas.utility import APIResponse

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
    background_tasks.add_task(scrape_task, db, str(request.url), request.category, request.tags)
    return APIResponse(message="Scraping has been initiated in the background.")

@router.get("/", response_model=APIResponse)
def read_trends(
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of scraped trends.
    """
    trends = trend_service.get_trends(db)
    trends_response = [TrendData.from_orm(trend) for trend in trends]
    return APIResponse(message="Scraped trends retrieved successfully", data=trends_response)
