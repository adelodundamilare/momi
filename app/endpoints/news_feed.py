from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.news_feed import NewsFeed
from app.services.news_feed import NewsFeedService
from app.services.scraper import ScraperAPIScraper
from app.schemas.utility import APIResponse
from app.utils.deps import get_current_user
from app.models.user import User
from app.crud.bookmarked_news import bookmarked_news
from app.schemas.bookmarked_news import BookmarkedNewsCreate
from app.models.news_feed import NewsFeed as NewsFeedModel
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
    current_user: User = Depends(get_current_user) # Protected endpoint
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
    skip: int = 0,
    limit: int = 100
):
    """
    Retrieve a list of news feed items with pagination.
    """
    try:
        news_items = news_feed_service.get_news(db, skip=skip, limit=limit)
        news_feed_response = [NewsFeed.from_orm(item) for item in news_items]
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
    # Check if news item exists
    news_item = db.query(NewsFeedModel).filter(NewsFeedModel.id == news_id).first()
    if not news_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="News item not found")

    # Check if already bookmarked
    existing_bookmark = db.query(bookmarked_news.model).filter(
        bookmarked_news.model.user_id == current_user.id,
        bookmarked_news.model.news_feed_id == news_id
    ).first()
    if existing_bookmark:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="News item already bookmarked")

    try:
        obj_in = BookmarkedNewsCreate(user_id=current_user.id, news_feed_id=news_id)
        bookmarked_news.create(db, obj_in=obj_in)
        return APIResponse(message="News item bookmarked successfully")
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
        bookmarked = db.query(NewsFeedModel).join(bookmarked_news.model).filter(bookmarked_news.model.user_id == current_user.id).all()
        bookmarked_response = [NewsFeed.from_orm(b) for b in bookmarked]
        return APIResponse(message="Bookmarked news retrieved successfully", data=bookmarked_response)
    except Exception as e:
        logger.error(f"Error in get_bookmarked_news: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
