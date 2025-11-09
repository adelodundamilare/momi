from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.conversation import Conversation
from app.schemas.conversation import ConversationCreate, ConversationUpdate

class CRUDConversation(CRUDBase[Conversation, ConversationCreate, ConversationUpdate]):
    def get_by_user_id(self, db: Session, *, user_id: int) -> List[Conversation]:
        return db.query(self.model).filter(self.model.user_id == user_id).all()

    def get_by_user_id_sorted(self, db: Session, *, user_id: int) -> List[Conversation]:
        return db.query(self.model).filter(self.model.user_id == user_id).order_by(self.model.created_at.desc()).all()

    def get_by_id_and_user(self, db: Session, *, conversation_id: int, user_id: int) -> Optional[Conversation]:
        return db.query(self.model).filter(
            self.model.id == conversation_id,
            self.model.user_id == user_id
        ).first()

conversation = CRUDConversation(Conversation)
