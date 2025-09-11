from app.crud.base import CRUDBase
from app.models.news_feed import NewsFeed
from app.schemas.news_feed import NewsFeedCreate, NewsFeedUpdate

class CRUDNewsFeed(CRUDBase[NewsFeed, NewsFeedCreate, NewsFeedUpdate]):
    pass

news_feed = CRUDNewsFeed(NewsFeed)