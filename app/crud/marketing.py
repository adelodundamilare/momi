from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.marketing import MarketingCopy as MarketingCopyModel
from app.schemas.marketing import MarketingCopyCreate, MarketingCopy as MarketingCopySchema


class CRUDMarketingCopy(CRUDBase[MarketingCopyModel, MarketingCopyCreate, MarketingCopySchema]):
    # Overriding create to bypass Pydantic validation on the SQLAlchemy model
    def create(self, db: Session, *, obj_in: MarketingCopyCreate) -> MarketingCopyModel:
        db_obj = MarketingCopyModel(
            product_name=obj_in.product_name,
            tagline=obj_in.tagline,
            key_features=obj_in.key_features,
            marketing_copy=obj_in.marketing_copy,
            product_mockup_url=obj_in.product_mockup_url,
            formula_id=obj_in.formula_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


marketing_copy = CRUDMarketingCopy(MarketingCopyModel)
