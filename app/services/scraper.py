from abc import ABC, abstractmethod
import requests
import logging
from urllib.parse import urljoin
import feedparser
from typing import Optional, List, Dict, Any
import xml.etree.ElementTree as ET
from html import unescape
import re

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

    def _clean_title(self, title_text):
        """Clean title by removing CDATA tags and HTML entities"""
        if title_text.startswith('<![CDATA[') and title_text.endswith(']]>'):
            title_text = title_text[9:-3]  # Remove CDATA wrapper
        title_text = re.sub(r'\s*\(TrendHunter\.com\)\s*', '', title_text)
        return unescape(title_text)

    def _clean_description(self, desc_text):
        """Clean description by removing CDATA, HTML tags, and extracting clean text"""
        if desc_text.startswith('<![CDATA[') and desc_text.endswith(']]>'):
            desc_text = desc_text[9:-3]  # Remove CDATA wrapper

        # Remove HTML tags but keep the text content
        desc_text = re.sub(r'<[^>]+>', '', desc_text)
        desc_text = re.sub(r'\s*\(TrendHunter\.com\)\s*', '', desc_text)

        # Clean up extra whitespace
        desc_text = ' '.join(desc_text.split())

        return unescape(desc_text)

    def fetch_food_trends(self, rss_url: str) -> List[Dict]:
        articles = []
        try:
            response = self._make_request(rss_url, timeout=30)
            response_text = response.text
            root = ET.fromstring(response_text)
            feeds = root.findall('.//item')

            for item in feeds:
                title = item.find('title')
                link = item.find('link')
                description = item.find('description')
                pub_date = item.find('pubDate')
                enclosure = item.find('enclosure')

                item_data = {
                    'title': self._clean_title(title.text) if title is not None else None,
                    'link': link.text if link is not None else None,
                    'description': self._clean_description(description.text) if description is not None else None,
                    'pubDate': pub_date.text if pub_date is not None else None,
                    'enclosure': enclosure.get('url') if enclosure is not None else None
                }

                articles.append(item_data)
        except requests.RequestException as e:
            logger.error(f"Error fetching RSS feed {rss_url}: {e}")
        except Exception as e:
            logger.error(f"Error parsing RSS feed {rss_url}: {e}")

        return articles
