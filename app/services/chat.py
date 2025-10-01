from typing import List, Iterator
from sqlalchemy.orm import Session

from app.core.config import settings
from app.schemas.chat import Message
from app.crud.trend import trend as trend_crud
from app.crud.ingredient import ingredient as ingredient_crud
from app.crud.chat import chat_history as chat_history_crud # Import chat_history_crud
from app.services.ai_provider import AIProvider, OpenAIProvider
from app.utils import prompt_templates
from app.models.chat import ChatHistory as ChatHistoryModel # Import SQLAlchemy model

class ChatService:
    def __init__(self, ai_provider: AIProvider = OpenAIProvider()): # Inject the provider
        self.ai_provider = ai_provider

    def _retrieve_context(self, query: str, db: Session) -> str:
        context_parts = []

        # Search for relevant trends
        trends = trend_crud.get_multi(db, search=query, limit=2) # Limit to 2 relevant trends
        if trends:
            context_parts.append("Relevant Trends:\n")
            for trend in trends:
                context_parts.append(f"- Title: {trend.title}\n  Content: {trend.content[:200]}...") # Truncate content

        # Search for relevant ingredients
        ingredients = ingredient_crud.get_multi(db, search=query, limit=2) # Limit to 2 relevant ingredients
        if ingredients:
            context_parts.append("Relevant Ingredients:\n")
            for ingredient in ingredients:
                context_parts.append(f"- Name: {ingredient.name}\n  Description: {ingredient.description[:200]}...") # Truncate description

        return "\n".join(context_parts)

    def send_streaming_message(self, messages: List[Message], db: Session, agent_type: str = "innovative") -> Iterator[str]:
        """
        Calls the AI provider in streaming mode and yields the content chunks.
        """
        latest_user_message = messages[-1].content if messages and messages[-1].role == "user" else ""
        context = self._retrieve_context(latest_user_message, db)

        if agent_type == "innovative":
            system_prompt = prompt_templates.INNOVATIVE_AGENT_SYSTEM_PROMPT.format(context=context)
        elif agent_type == "compliance":
            system_prompt = prompt_templates.COMPLIANCE_AGENT_SYSTEM_PROMPT.format(context=context)
        else:
            system_prompt = prompt_templates.DEFAULT_AGENT_SYSTEM_PROMPT.format(context=context)

        # Prepend the system prompt to the messages list
        messages_for_ai = [Message(role="system", content=system_prompt)] + messages
        
        return self.ai_provider.generate_chat_completion(messages_for_ai)

    def get_user_chat_history(self, db: Session, user_id: int) -> List[ChatHistoryModel]:
        return chat_history_crud.get_by_user_id(db, user_id=user_id)

