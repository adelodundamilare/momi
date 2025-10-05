from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from app.schemas.commercial_workflow_analysis import Risk, Recommendation, Task, AITimelineOutput

# --- For generate_summary_and_sentiment ---
class AISummaryAndSentiment(BaseModel):
    summary: str
    sentiment: str

# --- For generate_trend_signals ---
class AITrendSignals(BaseModel):
    signals: List[str]

# --- For AI-powered trend extraction ---
class AITrendData(BaseModel):
    title: str
    summary: str
    keywords: List[str]
    category: str
    sentiment: str
    impact_score: int = Field(..., ge=1, le=10)

# --- For generate_trend_category_and_tags ---
class AITrendCategoryAndTags(BaseModel):
    category: str = Field(...)
    tags: List[str] = Field(...)

# --- For generate_ingredient_enrichment ---
class AIIngredientEnrichment(BaseModel):
    description: Optional[str] = None
    benefits: Optional[str] = None
    claims: Optional[str] = None
    regulatory_notes: Optional[str] = None
    function: Optional[str] = None
    weight: Optional[int] = None
    unit: Optional[str] = None
    allergies: Optional[str] = None

# --- For generate_insight_portal_data ---
class AISharedProductConcept(BaseModel):
    image: str
    title: str
    key_ingredients: List[str]

class AIAssistantRecommendations(BaseModel):
    opportunity: str
    risk: str

class AIGenderBias(BaseModel):
    male: float
    female: float

class AIInsightPortalData(BaseModel):
    shared_product_concepts: List[AISharedProductConcept]
    company_competitors: List[str]
    assistant_recommendations: AIAssistantRecommendations
    demography_data: Dict[str, int]
    gender_bias: AIGenderBias
    top_geographic_locations: List[str]

# --- For generate_formula_details ---
class AIFormulaIngredient(BaseModel):
    name: str
    quantity: float
    estimated_cost: float = Field(..., alias='estimated_cost')

class AIFormulaDetails(BaseModel):
    formula_name: str
    formula_description: str
    ingredients: List[AIFormulaIngredient]

# --- For Commercialization Workflow Analysis ---
class AICommercializationInsights(BaseModel):
    timeline_data: AITimelineOutput
    risks: List[Risk]
    recommendations: List[Recommendation]
