from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, List, Tuple

from app.crud.base import CRUDBase
from app.models.news_feed import NewsFeed
from app.schemas.news_feed import NewsFeedCreate, NewsFeedUpdate

class CRUDNewsFeed(CRUDBase[NewsFeed, NewsFeedCreate, NewsFeedUpdate]):
    def get_by_slug(self, db: Session, *, slug: str) -> Optional[NewsFeed]:
        return db.query(self.model).filter(self.model.slug == slug).first()

    def get_multi_with_bookmarks(self, db: Session, *, user_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List:
        """Get news feed items with bookmark status for user."""
        from app.crud.bookmarked_news import bookmarked_news

        if user_id:
            result = db.query(self.model).outerjoin(
                bookmarked_news.model,
                and_(
                    bookmarked_news.model.news_feed_id == self.model.id,
                    bookmarked_news.model.user_id == user_id
                )
            ).add_columns(
                bookmarked_news.model.id.isnot(None).label('is_bookmarked')
            ).offset(skip).limit(limit).all()

            return [(item[0], bool(item[1])) for item in result]
        else:
            return db.query(self.model).offset(skip).limit(limit).all()

news_feed = CRUDNewsFeed(NewsFeed)
