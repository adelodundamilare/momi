from typing import Dict, Any, List
from app.services.ai_provider import AIProvider, OpenAIProvider

class InsightPortalService:
    def __init__(self, ai_provider: AIProvider = OpenAIProvider()):
        self.ai_provider = ai_provider

    def generate_portal_insights(self, ingredient_name: str) -> Dict[str, Any]:
        # This method will call the AI provider to generate the insights
        # for the insight portal.
        return self.ai_provider.generate_insight_portal_data(ingredient_name)
