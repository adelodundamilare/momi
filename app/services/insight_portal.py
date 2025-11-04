from typing import Any, Optional
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
        return await self.generate_portal_insights_with_context(ingredient_name, None)

    async def generate_portal_insights_with_context(
        self,
        ingredient_name: str,
        chat_context: Optional[str] = None
    ) -> AIInsightPortalData:
        """
        Generates insights for the portal with optional chat context for personalization.

        Args:
            ingredient_name: The ingredient to analyze
            chat_context: Optional chat conversation context for personalized insights

        Returns:
            AIInsightPortalData: Structured insight data

        Raises:
            HTTPException: If AI service fails
        """
        try:
            if chat_context:
                # Use contextual prompt
                insight_data = await self.ai_provider.generate_insight_portal_data_with_context(
                    ingredient_name, chat_context
                )
            else:
                # Use standard prompt
                insight_data = await self.ai_provider.generate_insight_portal_data(ingredient_name)

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
