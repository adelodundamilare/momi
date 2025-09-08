from typing import List, Iterator
from sqlalchemy.orm import Session

from app.core.config import settings
from app.schemas.chat import Message
from app.crud.trend import trend as trend_crud
from app.crud.ingredient import ingredient as ingredient_crud
from app.services.ai_provider import AIProvider, OpenAIProvider # Import the new provider

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

    def send_streaming_message(self, messages: List[Message], db: Session) -> Iterator[str]:
        """
        Calls the AI provider in streaming mode and yields the content chunks.
        """
        latest_user_message = messages[-1].content if messages and messages[-1].role == "user" else ""
        context = self._retrieve_context(latest_user_message, db)

        system_prompt = (
            "You are a food innovation expert. Your goal is to provide helpful and concise answers "
            "based on the provided context. If the context does not contain enough information, "
            "state that you don't have enough information to answer the question. "
            "Do not make up information. "
            "Context:\n" + context
        )

        # Prepend the system prompt to the messages list
        messages_for_ai = [Message(role="system", content=system_prompt)] + messages
        
        return self.ai_provider.generate_chat_completion(messages_for_ai)
