from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.bookmarked_news import BookmarkedNews
from app.schemas.bookmarked_news import BookmarkedNewsCreate

class CRUDBookmarkedNews(CRUDBase[BookmarkedNews, BookmarkedNewsCreate, None]):
    def get_by_user_and_news(self, db: Session, *, user_id: int, news_feed_id: int):
        """Get bookmark by user and news item."""
        return db.query(self.model).filter(
            self.model.user_id == user_id,
            self.model.news_feed_id == news_feed_id
        ).first()

    def exists_by_user_and_news(self, db: Session, *, user_id: int, news_feed_id: int) -> bool:
        """Check if bookmark exists for user and news item."""
        return db.query(self.model).filter(
            self.model.user_id == user_id,
            self.model.news_feed_id == news_feed_id
        ).first() is not None

    def get_bookmarked_news_for_user(self, db: Session, *, user_id: int):
        """Get all bookmarked news items for a user."""
        from app.crud.news_feed import news_feed as news_feed_crud

        return db.query(news_feed_crud.model).join(
            self.model
        ).filter(
            self.model.user_id == user_id
        ).all()

bookmarked_news = CRUDBookmarkedNews(BookmarkedNews)
