from pydantic import BaseModel
from typing import List, Dict

class InsightPortal(BaseModel):
    top_ingredient_mentions: Dict[str, Dict[str, int]]
    shared_product_concepts: List[str]
    company_competitors: List[str]
    assistant_recommendations: List[str]
    demography_data: Dict[str, int]
    gender_bias: Dict[str, float]
    top_geographic_locations: List[str]
