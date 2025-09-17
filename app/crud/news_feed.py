from sqlalchemy.orm import Session
from typing import Optional

from app.crud.base import CRUDBase
from app.models.news_feed import NewsFeed
from app.schemas.news_feed import NewsFeedCreate, NewsFeedUpdate

class CRUDNewsFeed(CRUDBase[NewsFeed, NewsFeedCreate, NewsFeedUpdate]):
    def get_by_slug(self, db: Session, *, slug: str) -> Optional[NewsFeed]:
        return db.query(self.model).filter(self.model.slug == slug).first()

news_feed = CRUDNewsFeed(NewsFeed)