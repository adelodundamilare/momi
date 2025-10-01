from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from email.utils import parsedate_to_datetime

from app.crud.news_feed import news_feed as news_feed_crud
from app.schemas.news_feed import NewsFeedCreate, NewsFeed
from app.services.scraper import Scraper
from app.utils.text_utils import generate_slug

class NewsFeedService:
    FOOD_DIVE_RSS_FEED_URL = "https://www.fooddive.com/feeds/news/"

    def __init__(self, scraper: Scraper):
        self.scraper = scraper

    def _parse_pub_date(self, pubDate_str: str, title: str) -> Optional[datetime]:
        """Parses a pubDate string into a datetime object."""
        if not pubDate_str:
            return None
        try:
            return parsedate_to_datetime(pubDate_str)
        except (ValueError, TypeError):
            print(f"Warning: Could not parse pubDate '{pubDate_str}' for news '{title}'. Setting to None.")
            return None

    async def fetch_and_process_news(self, db: Session):
        print(f"Fetching articles from RSS feed: {self.FOOD_DIVE_RSS_FEED_URL}")
        articles = self.scraper.fetch_food_news(self.FOOD_DIVE_RSS_FEED_URL)
        print(f"Found {len(articles)} news articles")

        for entry in articles:
            if not entry["title"] or not entry["link"]:
                continue

            slug = generate_slug(entry["title"])
            if news_feed_crud.get_by_slug(db, slug=slug):
                # print(f"Skipping duplicate news: {entry["title"]}")
                continue

            news_data_create = NewsFeedCreate(
                title=entry["title"],
                slug=slug,
                source="Food Dive", # Hardcode the source
                url=entry["link"],
                image=entry["image"],
                published_at=self._parse_pub_date(entry["pubDate"], entry["title"])
            )

            try:
                news_feed_crud.create(db, obj_in=news_data_create)
            except Exception as e:
                print(f"Error processing news from {entry['link']}: {e}")

    def get_news(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[NewsFeed]:
        """Retrieve news with pagination."""
        return news_feed_crud.get_multi(db, skip=skip, limit=limit)

