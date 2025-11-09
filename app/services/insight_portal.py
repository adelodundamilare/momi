from typing import Any, Optional, List
from sqlalchemy.orm import Session
from app.services.ai_provider import AIProvider, AIProviderError
from app.schemas.ai_responses import AIInsightPortalData
from app.crud.conversation import conversation as conversation_crud
from app.crud.chat_message import chat_message
from fastapi import HTTPException, status

class InsightPortalService:
    def __init__(self, ai_provider: AIProvider):
        self.ai_provider = ai_provider

    async def generate_portal_insights(self, ingredient_name: str) -> AIInsightPortalData:
        return await self.generate_portal_insights_with_context(ingredient_name, None)

    async def generate_portal_insights_with_context(
        self,
        ingredient_name: str,
        chat_context: Optional[str] = None
    ) -> AIInsightPortalData:
        try:
            if chat_context:
                insight_data = await self.ai_provider.generate_insight_portal_data_with_context(
                    ingredient_name, chat_context
                )
            else:
                insight_data = await self.ai_provider.generate_insight_portal_data(ingredient_name)

            if not insight_data:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="AI service returned no data for the insight portal."
                )
            return insight_data
        except AIProviderError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"A critical error occurred with the AI service while generating insights: {e}"
            )

    def create_chat_context_for_insights(self, db: Session, conversation_id: int, user_id: int) -> str:
        conversation = conversation_crud.get_by_id_and_user(db, conversation_id=conversation_id, user_id=user_id)
        if not conversation:
            raise ValueError("Conversation not found or access denied")

        messages = chat_message.get_by_conversation_id(db, conversation_id=conversation_id)
        return self._process_conversation_messages(messages)

    def _process_conversation_messages(self, messages: List[Any]) -> str:
        if not messages:
            return "No conversation history available."

        full_conversation = self._create_chronological_narrative(messages)
        trimmed_context = self._trim_to_token_limit(full_conversation, max_tokens=2000)

        return trimmed_context

    def _create_chronological_narrative(self, messages: List[Any]) -> str:
        conversation_parts = []

        for msg in messages[-50:]:
            role_prefix = "User:" if msg.role == "user" else "Assistant:"
            conversation_parts.append(f"{role_prefix} {msg.content}")

        return "\n".join(conversation_parts)

    def _trim_to_token_limit(self, text: str, max_tokens: int) -> str:
        estimated_tokens = len(text.split()) * 1.3

        if estimated_tokens <= max_tokens:
            return text

        words = text.split()
        max_words = int(max_tokens / 1.3)

        if len(words) <= max_words:
            return text

        truncated = words[-max_words:]
        return " ".join(truncated)
