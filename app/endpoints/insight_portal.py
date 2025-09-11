from fastapi import APIRouter, Depends
from app.schemas.insight_portal import InsightPortal
from app.schemas.utility import APIResponse

router = APIRouter()

@router.get("/", response_model=APIResponse)
def get_insight_portal():
    """
    Retrieve insights for the chat insight portal.
    """
    mock_data = {
        "top_ingredient_mentions": {
            "Turmeric": {"TikTok": 1500, "Instagram": 2500},
            "Ashwagandha": {"TikTok": 1200, "Instagram": 2000},
        },
        "shared_product_concepts": ["Calming beverage", "Focus-enhancing snack bar"],
        "company_competitors": ["Competitor A", "Competitor B"],
        "assistant_recommendations": ["Consider using Monk Fruit as a sweetener", "Explore sustainable packaging options"],
        "demography_data": {"18-24": 120, "25-34": 250, "35-44": 180},
        "gender_bias": {"male": 0.4, "female": 0.6},
        "top_geographic_locations": ["USA", "India", "UK"],
    }
    return APIResponse(message="Insight portal data retrieved successfully", data=mock_data)
