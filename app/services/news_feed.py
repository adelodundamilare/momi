from sqlalchemy.orm import Session
import requests
from bs4 import BeautifulSoup
from typing import List

from app.crud.news_feed import news_feed as news_feed_crud
from app.schemas.news_feed import NewsFeedCreate

class NewsFeedService:
    def scrape_and_save(self, db: Session, *, url: str, category: str | None = None, tags: List[str] | None = None):
        """
        Scrapes a URL, extracts title, content, and image, and saves to the news_feed table.
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status() # Raise an exception for bad status codes

            soup = BeautifulSoup(response.content, 'html.parser')

            title = soup.title.string if soup.title else 'No Title Found'
            
            # Extract featured image URL
            image_url = None
            og_image = soup.find("meta", property="og:image")
            if og_image and og_image.get("content"):
                image_url = og_image["content"]
            else:
                # Fallback to finding the first significant image in the body
                main_content = soup.find("body") # Or a more specific content div
                if main_content:
                    first_img = main_content.find("img")
                    if first_img and first_img.get("src"):
                        image_url = first_img["src"]

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

            news_data = NewsFeedCreate(
                title=title,
                source=url,
                url=url,
                image=image_url
            )
            news_feed_crud.create(db, obj_in=news_data)
            print(f"Successfully scraped and saved news: {url}")

        except requests.RequestException as e:
            print(f"Error during scraping news {url}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while processing news {url}: {e}")
