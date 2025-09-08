from sqlalchemy.orm import Session
import json
from typing import List

from app.core.config import settings
from app.crud.social_post import social_post as social_post_crud
from app.crud.consumer_insight import consumer_insight as consumer_insight_crud
from app.schemas.consumer_insight import ConsumerInsightCreate
from app.services.ai_provider import AIProvider, OpenAIProvider # Import the new provider

class ConsumerInsightService:
    def __init__(self, ai_provider: AIProvider = OpenAIProvider()): # Inject the provider
        self.ai_provider = ai_provider

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

        try:
            signals = self.ai_provider.generate_trend_signals(combined_content)

            for signal in signals:
                if isinstance(signal, str) and ("↑" in signal or "↓" in signal):
                    consumer_insight_crud.create(db, obj_in=ConsumerInsightCreate(
                        social_post_id=social_post_ids[0], # Link to the first post for simplicity, or iterate
                        insight_type="trend_signal",
                        signal_value=signal,
                        model_version=self.ai_provider.model # Use model from provider
                    ))
            print(f"Successfully generated and saved {len(signals)} trend signals.")

        except Exception as e:
            print(f"An error occurred while generating trend signals: {e}")
