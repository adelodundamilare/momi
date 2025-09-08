from sqlalchemy.orm import Session

from app.crud.trend import trend as trend_crud
from app.crud.ai_insight import insight as insight_crud
from app.schemas.ai_insight import InsightCreate
from app.services.ai_provider import AIProvider, OpenAIProvider # Import the new provider

class AIInsightService:
    def __init__(self, ai_provider: AIProvider = OpenAIProvider()): # Inject the provider
        self.ai_provider = ai_provider

    def generate_and_save_insights(self, db: Session, trend_id: int):
        """
        Generates insights for a trend and saves them to the database.
        This is intended to be run in a background task.
        """
        trend = trend_crud.get(db, id=trend_id)
        if not trend or not trend.content:
            print(f"Trend with id {trend_id} not found or has no content.")
            return

        try:
            insights = self.ai_provider.generate_summary_and_sentiment(trend.content)
            summary = insights.get("summary", "No summary generated.")
            sentiment = insights.get("sentiment", "No sentiment generated.")

            # Save the summary
            insight_crud.create(db, obj_in=InsightCreate(
                trend_data_id=trend_id,
                insight_type="summary",
                content=summary,
                model_version=self.ai_provider.model # Use model from provider
            ))

            # Save the sentiment
            insight_crud.create(db, obj_in=InsightCreate(
                trend_data_id=trend_id,
                insight_type="sentiment",
                content=sentiment,
                model_version=self.ai_provider.model # Use model from provider
            ))

            print(f"Successfully generated and saved insights for trend {trend_id}")

        except Exception as e:
            print(f"An error occurred while generating insights for trend {trend_id}: {e}")
