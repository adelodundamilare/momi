from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import asyncio
from datetime import datetime
from email.utils import parsedate_to_datetime

from app.crud.trend import trend as trend_crud
from app.schemas.trend import TrendDataCreate
from app.services.scraper import Scraper # Import the Scraper interface
from app.utils.text_utils import generate_slug # Import generate_slug

class TrendService:
    TRENDHUNTER_RSS_FEED_URL = "https://www.trendhunter.com/rss/category/Food-Trends"

    def __init__(self, scraper: Scraper): # Restore scraper dependency
        self.scraper = scraper

    def _parse_pub_date(self, pubDate_str: str, title: str) -> Optional[datetime]:
        """Parses a pubDate string into a datetime object."""
        pub_date: Optional[datetime] = None
        try:
            pub_date = datetime.strptime(pubDate_str, "%a, %d %b %Y %H:%M:%S %z")
        except ValueError:
            print(f"Warning: Could not parse pubDate '{pubDate_str}' for trend '{title}' with strptime. Attempting fallback.")
            try:
                pub_date = parsedate_to_datetime(pubDate_str)
            except (ValueError, TypeError):
                print(f"Warning: Could not parse pubDate '{pubDate_str}' for trend '{title}' with parsedate_to_datetime either. Setting to None.")
                pub_date = None
        return pub_date

    async def fetch_and_process_trends(self, db: Session): # Remove scraper from method signature
        print(f"Fetching articles from RSS feed: {self.TRENDHUNTER_RSS_FEED_URL}")
        articles = self.scraper.fetch_food_trends(self.TRENDHUNTER_RSS_FEED_URL) # Correct method call
        print(f"Found {len(articles)} articles")

        for entry in articles:
            link = entry["link"]
            title = entry["title"]
            description = entry["description"]
            pubDate_str = entry["pubDate"]
            image = entry["enclosure"]

            # Generate slug
            slug = generate_slug(title)

            # Check for duplicate slug
            existing_trend = trend_crud.get_by_slug(db, slug=slug)
            if existing_trend:
                print(f"Skipping duplicate trend: {title} (slug: {slug})")
                continue # Skip to the next entry

            # Convert pubDate string to datetime object using the helper function
            pub_date = self._parse_pub_date(pubDate_str, title)

            trend_data_create = TrendDataCreate(
                link=link,
                title=title,
                slug=slug, # Assign the generated slug
                description=description,
                pub_date=pub_date,
                image=image
            )

            try:
                trend_crud.create(db, obj_in=trend_data_create)
                print(f"Successfully processed and saved trend from: {link}")
            except Exception as e:
                print(f"Error processing trend from {link}: {e}")

    def get_trends(self, db: Session):
        return db.query(trend_crud.model).order_by(trend_crud.model.scraped_at.desc()).all()