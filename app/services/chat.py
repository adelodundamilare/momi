from typing import List, Iterator
import openai
from sqlalchemy.orm import Session

from app.core.config import settings
from app.schemas.chat import Message
from app.crud.trend import trend as trend_crud
from app.crud.ingredient import ingredient as ingredient_crud

class ChatService:
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

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
        Calls the OpenAI API in streaming mode and yields the content chunks.
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
        messages_for_openai = [Message(role="system", content=system_prompt)] + messages
        message_dicts = [msg.dict() for msg in messages_for_openai]

        try:
            stream = self.client.chat.completions.create(
                model="gpt-4", # Or another model like "gpt-3.5-turbo"
                messages=message_dicts,
                stream=True,
            )
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
        except Exception as e:
            print(f"OpenAI API error: {e}")
            yield "Error: Could not connect to the AI service."
