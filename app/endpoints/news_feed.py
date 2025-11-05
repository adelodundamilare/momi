from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.services.news_feed import NewsFeedService
from app.services.scraper import ScraperAPIScraper
from app.schemas.utility import APIResponse
from app.utils.deps import get_current_user, get_current_user_optional
from app.models.user import User
from app.utils.logger import setup_logger

logger = setup_logger("news_feed_api", "news_feed.log")

router = APIRouter()

# Instantiate dependencies
scraper = ScraperAPIScraper()
news_feed_service = NewsFeedService(scraper=scraper)

@router.post("/fetch-and-process", response_model=APIResponse)
async def fetch_and_process_news(
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: User = Depends(get_current_user)
):
    """
    Initiate fetching and processing of news from the Food Dive RSS feed.
    """
    try:
        background_tasks.add_task(news_feed_service.fetch_and_process_news, db)
        return APIResponse(message="News feed fetching and processing initiated.")
    except Exception as e:
        logger.error(f"Error initiating news fetch: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/", response_model=APIResponse)
def read_news_feed(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=200, description="Number of items to return")
):
    """
    Retrieve a list of news feed items with pagination and bookmark status.
    """
    try:
        news_feed_response = news_feed_service.get_news_with_bookmarks(
            db, user_id=current_user.id if current_user else None, skip=skip, limit=limit
        )

        return APIResponse(message="News feed retrieved successfully", data=news_feed_response)
    except Exception as e:
        logger.error(f"Error in read_news_feed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/{news_id}/bookmark", response_model=APIResponse)
def bookmark_news(
    news_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Bookmark a news item for the current user.
    """
    try:
        news_feed_service.bookmark_news_for_user(
            db, news_id=news_id, user_id=current_user.id
        )
        return APIResponse(message="News item bookmarked successfully")
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        elif "already bookmarked" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error in bookmark_news: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/bookmarked", response_model=APIResponse)
def get_bookmarked_news(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve bookmarked news items for the current user.
    """
    try:
        bookmarked_response = news_feed_service.get_bookmarked_news(
            db, user_id=current_user.id
        )
        return APIResponse(message="Bookmarked news retrieved successfully", data=bookmarked_response)
    except Exception as e:
        logger.error(f"Error in get_bookmarked_news: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
