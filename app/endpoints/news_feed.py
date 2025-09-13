from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.news_feed import NewsFeed
from app.crud.news_feed import news_feed
from app.schemas.utility import APIResponse
from app.schemas.trend import ScrapeRequest # Re-using ScrapeRequest for consistency
from app.services.news_feed import NewsFeedService
from app.utils.deps import get_current_user
from app.models.user import User
from app.crud.bookmarked_news import bookmarked_news
from app.schemas.bookmarked_news import BookmarkedNewsCreate
from app.models.news_feed import NewsFeed as NewsFeedModel

router = APIRouter()

news_feed_service = NewsFeedService()

def scrape_task(db: Session, url: str, category: str | None, tags: List[str] | None):
    news_feed_service.scrape_and_save(db, url=url, category=category, tags=tags)

@router.get("/", response_model=APIResponse)
def read_news_feed(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    Retrieve a list of news feed items with pagination.
    """
    news_feed_items = news_feed.get_multi(db, skip=skip, limit=limit)
    news_feed_response = [NewsFeed.from_orm(item) for item in news_feed_items]
    return APIResponse(message="News feed retrieved successfully", data=news_feed_response)

@router.post("/scrape", response_model=APIResponse)
def scrape_news(
    *, 
    db: Session = Depends(get_db), 
    request: ScrapeRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """
    Initiate scraping of a news URL in the background.
    """
    background_tasks.add_task(scrape_task, db, str(request.url), request.category, request.tags)
    return APIResponse(message="News scraping has been initiated in the background.")

@router.post("/{news_id}/bookmark", response_model=APIResponse)
def bookmark_news(
    news_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Bookmark a news item for the current user.
    """
    obj_in = BookmarkedNewsCreate(user_id=current_user.id, news_feed_id=news_id)
    bookmarked_news.create(db, obj_in=obj_in)
    return APIResponse(message="News item bookmarked successfully")

@router.get("/bookmarked", response_model=APIResponse)
def get_bookmarked_news(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve bookmarked news items for the current user.
    """
    bookmarked = db.query(NewsFeedModel).join(bookmarked_news.model).filter(bookmarked_news.model.user_id == current_user.id).all()
    bookmarked_response = [NewsFeed.from_orm(b) for b in bookmarked]
    return APIResponse(message="Bookmarked news retrieved successfully", data=bookmarked_response)
