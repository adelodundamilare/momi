from app.crud.base import CRUDBase
from app.models.ai_insight import Insight
from app.schemas.ai_insight import InsightCreate

# Insights are not meant to be updated via API
class CRUDInsight(CRUDBase[Insight, InsightCreate, None]):
    pass

insight = CRUDInsight(Insight)
