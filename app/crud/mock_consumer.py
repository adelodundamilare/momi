from app.crud.base import CRUDBase
from app.models.mock_consumer import MockConsumer
from app.schemas.mock_consumer import MockConsumerCreate

# Mock Consumers are not updated via API
class CRUDMockConsumer(CRUDBase[MockConsumer, MockConsumerCreate, None]):
    pass

mock_consumer = CRUDMockConsumer(MockConsumer)
