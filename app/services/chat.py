from typing import List, Iterator, Optional
from sqlalchemy.orm import Session

from app.core.config import settings
from app.schemas.chat import Message
from app.crud.trend import trend as trend_crud
from app.crud.ingredient import ingredient as ingredient_crud
from app.crud.conversation import conversation as conversation_crud
from app.crud.chat_message import chat_message as chat_message_crud
from app.services.ai_provider import AIProvider, OpenAIProvider
from app.utils import prompt_templates
from app.models.conversation import Conversation as ConversationModel
from app.schemas.conversation import ConversationCreate
from app.schemas.chat_message import ChatMessageCreate

class ChatService:
    def __init__(self, ai_provider: AIProvider = OpenAIProvider()):
        self.ai_provider = ai_provider

    def _retrieve_context(self, query: str, db: Session) -> str:
        context_parts = []

        trends = trend_crud.get_multi(db, search=query, limit=2)
        if trends:
            context_parts.append("Relevant Trends:\n")
            for trend in trends:
                context_parts.append(f"- Title: {trend.title}\n  Content: {(trend.description or '')[:200]}...")

        ingredients = ingredient_crud.get_multi(db, search=query, limit=2)
        if ingredients:
            context_parts.append("Relevant Ingredients:\n")
            for ingredient in ingredients:
                context_parts.append(f"- Name: {ingredient.name}\n  Description: {(ingredient.description or '')[:200]}...")

        return "\n".join(context_parts)

    def send_streaming_message(self, messages: List[Message], db: Session, agent_type: str, conversation_id: Optional[int], user_id: int) -> Iterator[str]:
        latest_user_message = messages[-1].content if messages and messages[-1].role == "user" else ""
        context = self._retrieve_context(latest_user_message, db)

        if agent_type == "innovative":
            system_prompt = prompt_templates.INNOVATIVE_AGENT_SYSTEM_PROMPT.format(context=context)
        elif agent_type == "compliance":
            system_prompt = prompt_templates.COMPLIANCE_AGENT_SYSTEM_PROMPT.format(context=context)
        else:
            system_prompt = prompt_templates.DEFAULT_AGENT_SYSTEM_PROMPT.format(context=context)

        messages_for_ai = [Message(role="system", content=system_prompt)] + messages
        
        if not conversation_id:
            conversation = conversation_crud.create(db, obj_in=ConversationCreate(user_id=user_id, title=latest_user_message[:50]))
            conversation_id = conversation.id
        
        for message in messages:
            chat_message_crud.create(db, obj_in=ChatMessageCreate(conversation_id=conversation_id, role=message.role, content=message.content))

        return self.ai_provider.generate_chat_completion(messages_for_ai)

    def get_user_conversations(self, db: Session, user_id: int) -> List[ConversationModel]:
        return conversation_crud.get_by_user_id(db, user_id=user_id)