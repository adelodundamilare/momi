from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import asyncio
from datetime import datetime

from app.crud.trend import trend as trend_crud
from app.schemas.trend import TrendDataCreate
from app.services.scraper import Scraper # Import the Scraper interface

class TrendService:
    TRENDHUNTER_RSS_FEED_URL = "https://www.trendhunter.com/rss/category/Food-Trends"

    def __init__(self, scraper: Scraper): # Restore scraper dependency
        self.scraper = scraper

    async def fetch_and_process_trends(self, db: Session): # Remove scraper from method signature
        print(f"Fetching articles from RSS feed: {self.TRENDHUNTER_RSS_FEED_URL}")
        articles = self.scraper.fetch_food_trends(self.TRENDHUNTER_RSS_FEED_URL) # Correct method call
        print(f"Found {len(articles)} articles")
        return

        for entry in articles:
            print(entry, 'entry')
            link = entry.link
            title = entry.title
            description = getattr(entry, 'summary', None)
            pub_date_str = getattr(entry, 'published', None)
            pub_date: Optional[datetime] = None
            if pub_date_str:
                try:
                    pub_date = datetime.strptime(pub_date_str, '%a, %d %b %Y %H:%M:%S %z')
                except ValueError:
                    print(f"Could not parse pubDate: {pub_date_str}")

            image = None
            if hasattr(entry, 'enclosures') and entry.enclosures:
                for enclosure in entry.enclosures:
                    if enclosure.get('type', '').startswith('image/'):
                        image = enclosure.get('href')
                        break

            trend_data_create = TrendDataCreate(
                link=link,
                title=title,
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