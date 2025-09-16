from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.trend import TrendData
from app.services.trend import TrendService
from app.schemas.utility import APIResponse
from app.utils.logger import setup_logger
from app.services.scraper import ScraperAPIScraper # Import Scraper type hint
from app.core.config import settings # Import settings

logger = setup_logger("trend_api", "trend.log")

router = APIRouter()

scraper = ScraperAPIScraper()

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
        trend_service = TrendService(scraper=scraper)
        background_tasks.add_task(trend_service.fetch_and_process_trends, db)
        return APIResponse(message="Trend fetching and processing initiated in the background.")
    except Exception as e:
        logger.error(f"Error in fetch_and_process_trends: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/", response_model=APIResponse)
def read_trends(
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of scraped trends.
    """
    try:
        trend_service = TrendService(scraper=scraper)
        trends = trend_service.get_trends(db)
        trends_response = [TrendData.from_orm(trend) for trend in trends]
        return APIResponse(message="Scraped trends retrieved successfully", data=trends_response)
    except Exception as e:
        logger.error(f"Error in read_trends: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))