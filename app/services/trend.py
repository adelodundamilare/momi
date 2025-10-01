from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from email.utils import parsedate_to_datetime
from fastapi import BackgroundTasks

from app.crud.trend import trend as trend_crud
from app.schemas.trend import TrendDataCreate, TrendCategory, TrendData
from app.services.scraper import Scraper
from app.services.ai_provider import AIProvider, OpenAIProvider
from app.utils.text_utils import generate_slug

class TrendService:
    TRENDHUNTER_RSS_FEED_URL = "https://www.trendhunter.com/rss/category/Food-Trends"

    def __init__(self, scraper: Scraper, ai_provider: AIProvider):
        self.scraper = scraper
        self.ai_provider = ai_provider

    def _parse_pub_date(self, pubDate_str: str, title: str) -> Optional[datetime]:
        """Parses a pubDate string into a datetime object."""
        try:
            return parsedate_to_datetime(pubDate_str)
        except (ValueError, TypeError):
            print(f"Warning: Could not parse pubDate '{pubDate_str}' for trend '{title}'. Setting to None.")
            return None

    async def _categorize_and_tag_trend(self, db: Session, trend_id: int):
        """Background task to enrich a trend with AI-generated category and tags."""
        print(f"Starting AI categorization for trend ID: {trend_id}")
        db_obj = trend_crud.get(db, id=trend_id)
        if not db_obj:
            print(f"Error: Trend with ID {trend_id} not found for AI processing.")
            return

        try:
            ai_data = await self.ai_provider.generate_trend_category_and_tags(
                article_title=db_obj.title,
                article_content=db_obj.description or ""
            )

            # Map AI category string to Enum, with a fallback
            try:
                category_enum = TrendCategory(ai_data.category.lower())
            except ValueError:
                category_enum = TrendCategory.UNCATEGORIZED
                print(f"Warning: AI-generated category '{ai_data.category}' was not in the predefined list. Falling back to UNCATEGORIZED.")

            update_data = {
                "category": category_enum.value,
                "tags": ai_data.tags
            }
            trend_crud.update(db, db_obj=db_obj, obj_in=update_data)
            print(f"Successfully categorized and tagged trend ID: {trend_id}")
        except Exception as e:
            print(f"Error during AI categorization for trend ID {trend_id}: {e}")

    async def fetch_and_process_trends(self, db: Session, background_tasks: BackgroundTasks):
        print(f"Fetching articles from RSS feed: {self.TRENDHUNTER_RSS_FEED_URL}")
        articles = self.scraper.fetch_food_trends(self.TRENDHUNTER_RSS_FEED_URL)
        print(f"Found {len(articles)} articles")

        for entry in articles:
            slug = generate_slug(entry["title"])
            if trend_crud.get_by_slug(db, slug=slug):
                print(f"Skipping duplicate trend: {entry['title']}")
                continue

            trend_data_create = TrendDataCreate(
                link=entry["link"],
                title=entry["title"],
                slug=slug,
                description=entry["description"],
                pub_date=self._parse_pub_date(entry["pubDate"], entry["title"]),
                image=entry["enclosure"]
            )

            try:
                new_trend = trend_crud.create(db, obj_in=trend_data_create)
                print(f"Successfully saved trend: {new_trend.title}")
                # Add the AI enrichment task to the background
                background_tasks.add_task(self._categorize_and_tag_trend, db, new_trend.id)
            except Exception as e:
                print(f"Error processing trend from {entry['link']}: {e}")

    def get_trends(self, db: Session, *, skip: int = 0, limit: int = 100, category: Optional[TrendCategory] = None, search: Optional[str] = None) -> List[TrendData]:
        """Retrieve trends with pagination, optional category filtering, and search."""
        return trend_crud.get_multi(db, skip=skip, limit=limit, category=category, search=search)
