from app.crud.base import CRUDBase
from app.models.marketing import MarketingCopy
from app.schemas.marketing import MarketingCopy as MarketingCopySchema

class CRUDMarketingCopy(CRUDBase[MarketingCopy, MarketingCopySchema, MarketingCopySchema]):
    pass

marketing_copy = CRUDMarketingCopy(MarketingCopy)
