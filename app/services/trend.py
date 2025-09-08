from sqlalchemy.orm import Session
import requests
from bs4 import BeautifulSoup

from app.crud.trend import trend as trend_crud
from app.schemas.trend import TrendDataCreate

class TrendService:
    def scrape_and_save(self, db: Session, *, url: str, category: str | None):
        """
        Scrapes a URL, extracts title and content, and saves to the database.
        This function is intended to be run in a background task.
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status() # Raise an exception for bad status codes

            soup = BeautifulSoup(response.content, 'html.parser')

            # A simple (naive) approach to get title and content
            title = soup.title.string if soup.title else 'No Title Found'
            
            # Remove script and style elements
            for script_or_style in soup(["script", "style"]):
                script_or_style.decompose()

            # Get text and clean it up
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            content = "\n".join(chunk for chunk in chunks if chunk)

            if not content:
                content = "No content could be extracted."

            trend_data = TrendDataCreate(
                source_url=url,
                title=title,
                content=content,
                category=category
            )
            trend_crud.create(db, obj_in=trend_data)
            print(f"Successfully scraped and saved: {url}")

        except requests.RequestException as e:
            print(f"Error during scraping {url}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while processing {url}: {e}")

    def get_trends(self, db: Session):
        # In a real app, you'd add pagination here
        return db.query(trend_crud.model).order_by(trend_crud.model.scraped_at.desc()).all()
