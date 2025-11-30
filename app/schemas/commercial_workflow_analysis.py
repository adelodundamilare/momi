from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import date

class Task(BaseModel):
    stage_name: str
    duration_weeks: float
    can_parallelize: bool
    dependencies: List[str]
    tasks: List[str]
    notes: str

class Risk(BaseModel):
    id: str
    category: str
    severity: str
    description: str
    impact_days: Optional[int] = None
    impact_cost: Optional[float] = None
    recommendation: str
    confidence: float

class Recommendation(BaseModel):
    id: str
    type: str
    title: str
    description: str
    cost_impact: Optional[float] = None
    time_impact: Optional[int] = None
    feasibility: str
    priority: str

class PackagingSpec(BaseModel):
    type: str
    size: str
    material: str
    supplier: Optional[str] = None

class AIWorkflowIngredient(BaseModel):
    name: str
    quantity: float
    unit: str
    supplier: Optional[str] = None
    lead_time_days: Optional[int] = None
    cost_per_unit: Optional[float] = None

class WorkflowRequest(BaseModel):
    product_id: str
    product_name: str
    ingredients: List[AIWorkflowIngredient]
    packaging: PackagingSpec
    target_volume: int
    batch_size: int
    target_launch_date: Optional[str] = None
    budget_limit: Optional[float] = None
    market: Optional[str] = "US"

class ParallelizationOpportunity(BaseModel):
    stages: List[str]
    savings_weeks: float
    feasibility: str

class AITimelineOutput(BaseModel):
    stages: List[Task]
    sequential_weeks: float
    optimized_weeks: float
    time_saved_weeks: float
    critical_path: List[str]
    parallelization_opportunities: List[ParallelizationOpportunity]

class CommercializationAnalysisOutput(BaseModel):
    product_id: str
    product_name: str
    generated_at: str
    timeline_data: AITimelineOutput
    risks: List[Risk]
    recommendations: List[Recommendation]
    supplier_analysis: Dict[str, Any]
    cost_analysis: Dict[str, Any]
    sustainability_score: Optional[Dict[str, Any]] = None

class TimelineAdjustmentRequest(BaseModel):
    stage_name: str
    duration_weeks: Optional[float] = None
    dependencies: Optional[List[str]] = None
    can_parallelize: Optional[bool] = None
    notes: Optional[str] = None

class UpdateTimelineRequest(BaseModel):
    adjustments: List[TimelineAdjustmentRequest]

class CommercialTimelineResponse(BaseModel):
    id: int
    formula_id: int
    timeline_data: Dict[str, Any]
    is_custom: bool
    created_at: str
    updated_at: str
