from pydantic import BaseModel
from typing import List
from datetime import date

class PricePoint(BaseModel):
    date: date
    price: float

class IngredientPriceChart(BaseModel):
    ingredient_id: int
    ingredient_name: str
    chart_data: List[PricePoint]
