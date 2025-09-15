from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.trend import TrendData
from app.schemas.trend import TrendDataCreate
from typing import Optional

# TrendData does not need an Update schema for now
class CRUDTrendData(CRUDBase[TrendData, TrendDataCreate, None]):
    def get_by_slug(self, db: Session, *, slug: str) -> Optional[TrendData]:
        return db.query(self.model).filter(self.model.slug == slug).first()

trend = CRUDTrendData(TrendData)
