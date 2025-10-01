from typing import Optional, List
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.chat import ChatHistory
from app.schemas.chat import ChatHistoryCreate, ChatHistoryUpdate

class CRUDChatHistory(CRUDBase[ChatHistory, ChatHistoryCreate, ChatHistoryUpdate]):
    def get_by_user_id(self, db: Session, *, user_id: int) -> List[ChatHistory]:
        return db.query(self.model).filter(self.model.user_id == user_id).all()

chat_history = CRUDChatHistory(ChatHistory)