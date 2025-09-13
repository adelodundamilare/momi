from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.insight_portal import InsightPortal, SocialPlatformMention
from app.schemas.utility import APIResponse
from app.core.database import get_db
from app.services.insight_portal import InsightPortalService
from app.utils.deps import get_current_user
from app.models.user import User
import random

router = APIRouter()

insight_portal_service = InsightPortalService()

@router.get("/", response_model=APIResponse)
def get_insight_portal(
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
        change_percentage = round(random.uniform(0.1, 5.0), 1) # 0.1% to 5.0% change
        change_sign = "+" if trend_direction == "up" else "-" if trend_direction == "down" else ""
        change_str = f"{change_sign}{change_percentage}%"

        top_ingredient_mentions[platform] = SocialPlatformMention(
            count=count,
            trend=trend_direction,
            change=change_str
        )

    # AI Analysis for other data (using a generic ingredient name for now)
    ai_generated_data = insight_portal_service.generate_portal_insights("General Ingredient")

    return APIResponse(
        message="Insight portal data retrieved successfully",
        data=InsightPortal(
            top_ingredient_mentions=top_ingredient_mentions,
            shared_product_concepts=ai_generated_data.get("shared_product_concepts", []),
            company_competitors=ai_generated_data.get("company_competitors", []),
            assistant_recommendations=ai_generated_data.get("assistant_recommendations", {}),
            demography_data=ai_generated_data.get("demography_data", {}),
            gender_bias=ai_generated_data.get("gender_bias", {}),
            top_geographic_locations=ai_generated_data.get("top_geographic_locations", []),
        )
    )
from app.schemas.utility import APIResponse
from app.core.database import get_db
from app.models.trend import TrendData
from sqlalchemy import func
from app.crud.ingredient import ingredient as ingredient_crud
from app.services.insight_portal import InsightPortalService
import random

router = APIRouter()

insight_portal_service = InsightPortalService()

@router.get("/{ingredient_slug}", response_model=APIResponse)
def get_insight_portal(
    ingredient_slug: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve insights for the chat insight portal based on an ingredient slug.
    """
    ingredient = ingredient_crud.get_by_slug(db, slug=ingredient_slug)
    if not ingredient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingredient not found")

    # Generate simple social response data (randomly)
    social_platforms = ["tiktok", "reddit", "instagram", "facebook", "x", "pinterest"]
    top_ingredient_mentions = {}
    for platform in social_platforms:
        count = random.randint(1000, 10000)
        trend_direction = random.choice(["up", "down", "stable"])
        change_percentage = round(random.uniform(0.1, 5.0), 1) # 0.1% to 5.0% change
        change_sign = "+" if trend_direction == "up" else "-" if trend_direction == "down" else ""
        change_str = f"{change_sign}{change_percentage}%"

        top_ingredient_mentions[platform] = SocialPlatformMention(
            count=count,
            trend=trend_direction,
            change=change_str
        )

    # AI Analysis for other data
    ai_generated_data = insight_portal_service.generate_portal_insights(ingredient.name)

    return APIResponse(
        message="Insight portal data retrieved successfully",
        data=InsightPortal(
            top_ingredient_mentions=top_ingredient_mentions,
            shared_product_concepts=ai_generated_data.get("shared_product_concepts", []),
            company_competitors=ai_generated_data.get("company_competitors", []),
            assistant_recommendations=ai_generated_data.get("assistant_recommendations", {}),
            demography_data=ai_generated_data.get("demography_data", {}),
            gender_bias=ai_generated_data.get("gender_bias", {}),
            top_geographic_locations=ai_generated_data.get("top_geographic_locations", []),
        )
    )
