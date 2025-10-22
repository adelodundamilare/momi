from pydantic import BaseModel, Field
from typing import List, Optional


class Nutrient(BaseModel):
    name: str = Field(..., description="Name of the nutrient, e.g., 'Total Fat' or 'Sodium'.")
    amount_per_serving: str = Field(..., description="The amount per serving, e.g., '10g' or '200mg'.")
    daily_value_percent: int = Field(..., description="The percentage of daily value, e.g., 15 for 15%.")


class EstimatedCost(BaseModel):
    amount: float
    currency: str
    description: str


class PotentialSavings(BaseModel):
    percentage: int
    description: str


class AllergenAlerts(BaseModel):
    detected: bool
    allergens: List[str]
    description: str


class Sustainability(BaseModel):
    score: float
    max_score: int
    factors: List[str]


class SupplierInfo(BaseModel):
    name: str
    index_score: int


class MarketingCopyBase(BaseModel):
    product_name: str
    tagline: str
    key_features: List[str]
    marketing_copy: str
    product_mockup_url: Optional[str] = None
    nutritional_facts: List[Nutrient]
    estimated_cost_per_unit: EstimatedCost
    batch_cost: EstimatedCost
    potential_savings: PotentialSavings
    suggestions: List[str]
    allergen_alerts: AllergenAlerts
    sustainability: Sustainability
    calories: Optional[int] = None
    serving_size_per_bottle: Optional[str] = None
    suppliers_index: Optional[List[SupplierInfo]] = None


class AIMarketingCopy(BaseModel):
    product_name: str = Field(..., description="A catchy and market-friendly name for the product.")
    tagline: str = Field(..., description="A short, memorable slogan for the product.")
    key_features: List[str] = Field(..., description="A list of 3-5 key selling points or features.", min_items=3, max_items=5)
    marketing_copy: str = Field(..., description="A compelling paragraph of marketing text for the product.")
    nutritional_facts: List[Nutrient] = Field(..., description="A list of key nutritional facts.")
    estimated_cost_per_unit: EstimatedCost = Field(..., description="Estimated cost per unit of the product.")
    batch_cost: EstimatedCost = Field(..., description="Estimated cost for a production batch.")
    potential_savings: PotentialSavings = Field(..., description="Potential cost savings.")
    suggestions: List[str] = Field(..., description="Suggestions for improvement or alternatives.")
    allergen_alerts: AllergenAlerts = Field(..., description="Allergen detection and alerts.")
    sustainability: Sustainability
    calories: Optional[int] = None
    serving_size_per_bottle: Optional[str] = None
    suppliers_index: Optional[List[SupplierInfo]] = None


class MarketingCopyCreate(MarketingCopyBase):
    formula_id: int


class MarketingCopy(MarketingCopyBase):
    id: int
    formula_id: int

    class Config:
        from_attributes = True
