from pydantic import BaseModel
from typing import List, Dict, Optional

class IngredientSocialMention(BaseModel):
    ingredient_name: str
    social_mentions: Dict[str, int]

class InsightPortal(BaseModel):
    top_ingredient_mentions: List[IngredientSocialMention]
    shared_product_concepts: List[str]
    company_competitors: List[str]
    assistant_recommendations: List[str]
    demography_data: Dict[str, int]
    gender_bias: Dict[str, float]
    top_geographic_locations: List[str]
