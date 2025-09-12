from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.insight_portal import InsightPortal, IngredientSocialMention
from app.schemas.utility import APIResponse
from app.core.database import get_db
from app.models.trend import TrendData
from sqlalchemy import func
from app.crud.ingredient import ingredient as ingredient_crud
from app.services.insight_portal import InsightPortalService

router = APIRouter()

insight_portal_service = InsightPortalService()

@router.get("/{ingredient_slug}", response_model=APIResponse)
def get_insight_portal(
    ingredient_slug: str,
    db: Session = Depends(get_db)
):
    """
    Retrieve insights for the chat insight portal based on an ingredient slug.
    """
    ingredient = ingredient_crud.get_by_slug(db, slug=ingredient_slug)
    if not ingredient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingredient not found")

    # Generate simple social response data (randomly)
    social_platforms = ["TikTok", "Instagram", "Twitter", "Reddit", "Facebook", "Pinterest"]
    top_ingredient_mentions = []
    for _ in range(3): # Generate data for 3 random platforms
        platform = random.choice(social_platforms)
        mentions = random.randint(100, 5000)
        
        # Generate random trend and percentage
        trend_direction = random.choice(["up", "down", "stable"])
        change_percentage = round(random.uniform(0.5, 20.0), 2) # 0.5% to 20% change

        top_ingredient_mentions.append(IngredientSocialMention(
            ingredient_name=ingredient.name,
            social_mentions={platform: mentions},
            trend=trend_direction,
            change_percentage=change_percentage
        ))

    # AI Analysis for other data
    ai_generated_data = insight_portal_service.generate_portal_insights(ingredient.name)

    return APIResponse(
        message="Insight portal data retrieved successfully",
        data=InsightPortal(
            top_ingredient_mentions=top_ingredient_mentions,
            shared_product_concepts=ai_generated_data.get("shared_product_concepts", []),
            company_competitors=ai_generated_data.get("company_competitors", []),
            assistant_recommendations=ai_generated_data.get("assistant_recommendations", []),
            demography_data=ai_generated_data.get("demography_data", {}),
            gender_bias=ai_generated_data.get("gender_bias", {}),
            top_geographic_locations=ai_generated_data.get("top_geographic_locations", []),
        )
    )
