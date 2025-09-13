from pydantic import BaseModel
from typing import List, Dict, Optional

class SocialPlatformMention(BaseModel):
    count: int
    trend: str
    change: str

class ProductConcept(BaseModel):
    image: str
    title: str
    key_ingredients: List[str]

class AssistantRecommendation(BaseModel):
    opportunity: str
    risk: str

class InsightPortal(BaseModel):
    top_ingredient_mentions: Dict[str, SocialPlatformMention]
    shared_product_concepts: List[ProductConcept]
    company_competitors: List[str]
    assistant_recommendations: AssistantRecommendation
    demography_data: Dict[str, int]
    gender_bias: Dict[str, float]
    top_geographic_locations: List[str]
