from sqlalchemy.orm import Session
import openai
import json
from typing import List

from app.core.config import settings
from app.crud.social_post import social_post as social_post_crud
from app.crud.consumer_insight import consumer_insight as consumer_insight_crud
from app.schemas.consumer_insight import ConsumerInsightCreate

class ConsumerInsightService:
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4-turbo" # Model that supports JSON mode

    def generate_trend_signals(self, db: Session, social_post_ids: List[int]):
        """
        Generates trend signals from social posts and saves them to the database.
        Intended to be run in a background task.
        """
        social_posts = []
        for post_id in social_post_ids:
            post = social_post_crud.get(db, id=post_id)
            if post:
                social_posts.append(f"Platform: {post.platform}, Author: {post.author}, Content: {post.content}")
        
        if not social_posts:
            print("No social posts found for the given IDs.")
            return

        combined_content = "\n---\n".join(social_posts)

        system_prompt = (
            "You are an expert in food and beverage market trends. Analyze the following social media posts "
            "and identify clear trend signals. A trend signal is a specific ingredient, product type, or concept "
            "that is showing a clear upward (↑) or downward (↓) trend. "
            "Respond with a JSON array of strings, where each string is a trend signal in the format '[Item] [↑/↓]'. "
            "Example: ["Moringa ↑", "Spirulina ↓", "Kombucha ↑"]."
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": combined_content}
                ]
            )

            # Expecting a JSON object with a key that contains the array of signals
            # Let's assume the key is 'signals' for robustness
            response_content = json.loads(response.choices[0].message.content)
            signals = response_content.get("signals", []) # Get the list of signals

            if not isinstance(signals, list):
                print(f"AI did not return a list of signals: {signals}")
                signals = [] # Ensure it's a list

            for signal in signals:
                if isinstance(signal, str) and ("↑" in signal or "↓" in signal):
                    consumer_insight_crud.create(db, obj_in=ConsumerInsightCreate(
                        social_post_id=social_post_ids[0], # Link to the first post for simplicity, or iterate
                        insight_type="trend_signal",
                        signal_value=signal,
                        model_version=self.model
                    ))
            print(f"Successfully generated and saved {len(signals)} trend signals.")

        except Exception as e:
            print(f"An error occurred while generating trend signals: {e}")
