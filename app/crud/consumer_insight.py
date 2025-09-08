from app.crud.base import CRUDBase
from app.models.consumer_insight import ConsumerInsight
from app.schemas.consumer_insight import ConsumerInsightCreate

class CRUDConsumerInsight(CRUDBase[ConsumerInsight, ConsumerInsightCreate, None]):
    pass

consumer_insight = CRUDConsumerInsight(ConsumerInsight)
