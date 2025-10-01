from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.crud.base import CRUDBase
from app.models.trend import TrendData
from app.schemas.trend import TrendDataCreate, TrendCategory
from typing import Optional, List

# TrendData does not need an Update schema for now
class CRUDTrendData(CRUDBase[TrendData, TrendDataCreate, None]):
    def get_by_slug(self, db: Session, *, slug: str) -> Optional[TrendData]:
        return db.query(self.model).filter(self.model.slug == slug).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100, category: Optional[TrendCategory] = None, search: Optional[str] = None
    ) -> List[TrendData]:
        query = db.query(self.model)
        if category:
            query = query.filter(self.model.category == category.value)
        if search:
            query = query.filter(or_(
                self.model.title.ilike(f"%{search}%"),
                self.model.description.ilike(f"%{search}%")
            ))
        return query.order_by(self.model.scraped_at.desc()).offset(skip).limit(limit).all()


trend = CRUDTrendData(TrendData)
