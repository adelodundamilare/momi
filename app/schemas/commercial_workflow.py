from pydantic import BaseModel
from typing import List, Optional
from datetime import date, timedelta

class TimelineStep(BaseModel):
    name: str
    start_date: date
    end_date: date

class CoManufacturer(BaseModel):
    name: str
    location: str

class CommercialWorkflowRequest(BaseModel):
    ingredient_availability: str # e.g., "readily available", "limited", "custom order"
    moq: str # e.g., "low", "medium", "high"
    supplier_region: str # e.g., "North America", "Europe", "Asia"

class CommercialWorkflowResponse(BaseModel):
    estimated_launch: date
    timeline_summary: str
    optimized_timeline: List[TimelineStep]
    ai_risk_callout: str
    timeline: List[TimelineStep]
    co_manufacturers: List[CoManufacturer]
