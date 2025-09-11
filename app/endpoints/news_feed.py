from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.news_feed import NewsFeed
from app.crud.news_feed import news_feed
from app.schemas.utility import APIResponse

router = APIRouter()

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
