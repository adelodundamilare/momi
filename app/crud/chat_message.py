from typing import List
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.chat_message import ChatMessage
from app.schemas.chat_message import ChatMessageCreate, ChatMessageUpdate

class CRUDChatMessage(CRUDBase[ChatMessage, ChatMessageCreate, ChatMessageUpdate]):
    def get_by_conversation_id(self, db: Session, *, conversation_id: int) -> List[ChatMessage]:
        return db.query(self.model).filter(self.model.conversation_id == conversation_id).all()

chat_message = CRUDChatMessage(ChatMessage)
