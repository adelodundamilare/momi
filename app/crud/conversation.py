from typing import List
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.conversation import Conversation
from app.schemas.conversation import ConversationCreate, ConversationUpdate

class CRUDConversation(CRUDBase[Conversation, ConversationCreate, ConversationUpdate]):
    def get_by_user_id(self, db: Session, *, user_id: int) -> List[Conversation]:
        return db.query(self.model).filter(self.model.user_id == user_id).all()

conversation = CRUDConversation(Conversation)
