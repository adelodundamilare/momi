from abc import ABC, abstractmethod
import requests
import logging
from urllib.parse import urljoin
import feedparser
from typing import Optional, List, Dict, Any

from app.core.config import settings

logger = logging.getLogger(__name__)

# Define a common User-Agent header
DEFAULT_REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/xml, text/xml, */*; q=0.01", # More appropriate for RSS/XML
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Accept-Encoding": "gzip, deflate, br",
}

class Scraper(ABC):
    """Abstract base class for web scraping services."""

    @abstractmethod
    def fetch_food_trends(self, rss_url: str) -> List[Dict]: # Corrected method name
        pass

class ScraperAPIScraper(Scraper):
    """Scraper implementation that routes requests through ScraperAPI."""

    def __init__(self):
        self.api_key=settings.SCRAPER_API_KEY
        self.base_url: str = settings.SCRAPER_API_BASE_URL # Use settings for base_url

        if not self.api_key:
            raise ValueError("ScraperAPI key must be provided for ScraperAPIScraper.")

    def _make_request(self, url: str, method: str = "GET", timeout: int = 10, **kwargs) -> requests.Response:
        session = requests.Session()
        session.headers.update(DEFAULT_REQUEST_HEADERS)

        payload = {"api_key": self.api_key, "url": url}
        if method == "GET":
            response = session.get(self.base_url, params=payload, timeout=timeout, **kwargs)
        else:
            raise NotImplementedError("ScraperAPI integration for non-GET methods not fully implemented yet.")

        response.raise_for_status()
        return response

    def fetch_food_trends(self, rss_url: str) -> List[Dict]:
        articles = []
        try:
            response = self._make_request(rss_url, timeout=10)
            feed = feedparser.parse(response.content)
            for entry in feed.entries:
                print(entry, 'entry')
                articles.append({
                    "title": entry.title if hasattr(entry, 'title') else 'No Title',
                    "link": entry.link if hasattr(entry, 'link') else 'No Link',
                    "summary": entry.summary if hasattr(entry, 'summary') else 'No Summary',
                })
        except requests.RequestException as e:
            logger.error(f"Error fetching RSS feed {rss_url}: {e}")
        except Exception as e:
            logger.error(f"Error parsing RSS feed {rss_url}: {e}")
        return articles
