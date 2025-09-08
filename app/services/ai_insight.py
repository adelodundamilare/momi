from sqlalchemy.orm import Session
import openai
import json

from app.core.config import settings
from app.crud.trend import trend as trend_crud
from app.crud.ai_insight import insight as insight_crud
from app.schemas.ai_insight import InsightCreate

class AIInsightService:
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4-turbo" # Specify the model that supports JSON mode

    def generate_and_save_insights(self, db: Session, trend_id: int):
        """
        Generates insights for a trend and saves them to the database.
        This is intended to be run in a background task.
        """
        trend = trend_crud.get(db, id=trend_id)
        if not trend or not trend.content:
            print(f"Trend with id {trend_id} not found or has no content.")
            return

        system_prompt = (
            "You are an expert analyst. Analyze the following article and provide a concise, "
            "one-paragraph summary and a sentiment analysis (either Positive, Negative, or Neutral). "
            "Respond with a JSON object containing two keys: 'summary' and 'sentiment'."
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": trend.content}
                ]
            )

            insights = json.loads(response.choices[0].message.content)
            summary = insights.get("summary", "No summary generated.")
            sentiment = insights.get("sentiment", "No sentiment generated.")

            # Save the summary
            insight_crud.create(db, obj_in=InsightCreate(
                trend_data_id=trend_id,
                insight_type="summary",
                content=summary,
                model_version=self.model
            ))

            # Save the sentiment
            insight_crud.create(db, obj_in=InsightCreate(
                trend_data_id=trend_id,
                insight_type="sentiment",
                content=sentiment,
                model_version=self.model
            ))

            print(f"Successfully generated and saved insights for trend {trend_id}")

        except Exception as e:
            print(f"An error occurred while generating insights for trend {trend_id}: {e}")
