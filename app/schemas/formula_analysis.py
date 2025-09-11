from pydantic import BaseModel
from typing import List

class FormulaAnalysis(BaseModel):
    estimated_cost_per_unit: float
    batch_cost: float
    savings_percentage: float
    allergy_alerts: List[str]
    sustainability_score: float
    suggestions: List[str]
