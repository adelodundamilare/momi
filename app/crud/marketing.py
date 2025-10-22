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
            formula_id=obj_in.formula_id,
            nutritional_facts=[fact.dict() for fact in obj_in.nutritional_facts],
            estimated_cost_per_unit=obj_in.estimated_cost_per_unit.dict(),
            batch_cost=obj_in.batch_cost.dict(),
            potential_savings=obj_in.potential_savings.dict(),
            suggestions=obj_in.suggestions,
            allergen_alerts=obj_in.allergen_alerts.dict(),
            sustainability=obj_in.sustainability.dict(),
            calories=obj_in.calories,
            serving_size_per_bottle=obj_in.serving_size_per_bottle,
            suppliers_index=[supplier.dict() for supplier in obj_in.suppliers_index] if obj_in.suppliers_index else []
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


marketing_copy = CRUDMarketingCopy(MarketingCopyModel)
