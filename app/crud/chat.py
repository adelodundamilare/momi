from app.crud.base import CRUDBase
from app.models.chat import ChatHistory
from app.schemas.chat import ChatHistoryCreate, ChatHistoryUpdate

class CRUDChatHistory(CRUDBase[ChatHistory, ChatHistoryCreate, ChatHistoryUpdate]):
    pass

chat_history = CRUDChatHistory(ChatHistory)