from app.crud.base import CRUDBase
from app.models.trend import TrendData
from app.schemas.trend import TrendDataCreate

# TrendData does not need an Update schema for now
class CRUDTrendData(CRUDBase[TrendData, TrendDataCreate, None]):
    pass

trend = CRUDTrendData(TrendData)
