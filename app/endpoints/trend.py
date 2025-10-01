from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.schemas.trend import TrendData, TrendCategory
from app.services.trend import TrendService
from app.schemas.utility import APIResponse
from app.utils.logger import setup_logger
from app.services.scraper import ScraperAPIScraper
from app.services.ai_provider import OpenAIProvider

logger = setup_logger("trend_api", "trend.log")

router = APIRouter()

# Instantiate dependencies once
scraper = ScraperAPIScraper()
ai_provider = OpenAIProvider()

@router.post("/fetch-and-process", response_model=APIResponse)
async def fetch_and_process_trends(
    *,
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks,
):
    """
    Initiate fetching and processing of trends from a hardcoded RSS feed in the background.
    """
    try:
        trend_service = TrendService(scraper=scraper, ai_provider=ai_provider)
        background_tasks.add_task(trend_service.fetch_and_process_trends, db, background_tasks)
        return APIResponse(message="Trend fetching and processing initiated in the background.")
    except Exception as e:
        logger.error(f"Error in fetch_and_process_trends: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/", response_model=APIResponse)
def read_trends(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=200, description="Number of items to return"),
    category: Optional[TrendCategory] = None,
    search: Optional[str] = Query(None, description="Search term for trend titles and descriptions")
):
    """
    Retrieve a list of scraped trends with pagination and category filtering.
    """
    try:
        
        trend_service = TrendService(scraper=scraper, ai_provider=ai_provider)
        trends = trend_service.get_trends(db, skip=skip, limit=limit, category=category)
        trends_response = [TrendData.from_orm(trend) for trend in trends]
        return APIResponse(message="Scraped trends retrieved successfully", data=trends_response)
    except Exception as e:
        logger.error(f"Error in read_trends: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))