from typing import Any
from app.services.ai_provider import AIProvider, AIProviderError
from app.schemas.ai_responses import AIInsightPortalData
from fastapi import HTTPException, status

class InsightPortalService:
    def __init__(self, ai_provider: AIProvider):
        self.ai_provider = ai_provider

    async def generate_portal_insights(self, ingredient_name: str) -> AIInsightPortalData:
        """
        Generates insights for the portal by calling the AI provider.
        Handles errors and returns a structured Pydantic model.
        """
        try:
            insight_data = await self.ai_provider.generate_insight_portal_data(ingredient_name)
            # The AI call now raises an exception on failure, so a None check is less likely
            # but good for defense. The custom exception is more descriptive.
            if not insight_data:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="AI service returned no data for the insight portal."
                )
            return insight_data
        except AIProviderError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"A critical error occurred with the AI service while generating insights: {e}"
            )