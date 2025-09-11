from app.crud.base import CRUDBase
from app.models.bookmarked_news import BookmarkedNews
from app.schemas.bookmarked_news import BookmarkedNewsCreate

class CRUDBookmarkedNews(CRUDBase[BookmarkedNews, BookmarkedNewsCreate, None]):
    pass

bookmarked_news = CRUDBookmarkedNews(BookmarkedNews)
