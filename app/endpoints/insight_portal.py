from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.insight_portal import InsightPortal, SocialPlatformMention
from app.schemas.utility import APIResponse
from app.core.database import get_db
from app.services.insight_portal import InsightPortalService
from app.services.ai_provider import OpenAIProvider
from app.utils.deps import get_current_user
from app.models.user import User
from app.utils.logger import setup_logger
import random

router = APIRouter()

logger = setup_logger("insight_portal", "account.log")
insight_portal_service = InsightPortalService(ai_provider=OpenAIProvider())

@router.get("/", response_model=APIResponse)
async def get_insight_portal(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve insights for the chat insight portal.
    """
    # Generate simple social response data (randomly)
    social_platforms = ["tiktok", "reddit", "instagram", "facebook", "x", "pinterest"]
    top_ingredient_mentions = {}
    for platform in social_platforms:
        count = random.randint(1000, 10000)
        trend_direction = random.choice(["up", "down", "stable"])
        change_percentage = round(random.uniform(0.1, 5.0), 1)
        change_sign = "+" if trend_direction == "up" else "-" if trend_direction == "down" else ""
        change_str = f"{change_sign}{change_percentage}%"

        top_ingredient_mentions[platform] = SocialPlatformMention(
            count=count,
            trend=trend_direction,
            change=change_str
        )

    # AI Analysis for other data
    ai_generated_data = await insight_portal_service.generate_portal_insights("General Ingredient")

    # Convert AI response models to dictionaries for InsightPortal model validation
    assistant_recommendations_dict = ai_generated_data.assistant_recommendations.model_dump()
    gender_bias_dict = ai_generated_data.gender_bias.model_dump()
    shared_product_concepts_list = [item.model_dump() for item in ai_generated_data.shared_product_concepts]

    return APIResponse(
        message="Insight portal data retrieved successfully",
        data=InsightPortal(
            top_ingredient_mentions=top_ingredient_mentions,
            shared_product_concepts=shared_product_concepts_list,
            company_competitors=ai_generated_data.company_competitors,
            assistant_recommendations=assistant_recommendations_dict,
            demography_data=ai_generated_data.demography_data,
            gender_bias=gender_bias_dict,
            top_geographic_locations=ai_generated_data.top_geographic_locations,
        )
    )
