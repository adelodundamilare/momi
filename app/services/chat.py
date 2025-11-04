from typing import List, Iterator, Optional
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.schemas.chat import Message
from app.crud.trend import trend as trend_crud
from app.crud.ingredient import ingredient as ingredient_crud
from app.crud.conversation import conversation as conversation_crud
from app.crud.chat_message import chat_message as chat_message_crud
from app.services.ai_provider import AIProvider, OpenAIProvider
from app.services.voice import VoiceService
from app.utils import prompt_templates
from app.models.conversation import Conversation as ConversationModel
from app.schemas.conversation import ConversationCreate
from app.schemas.chat_message import ChatMessageCreate

class ChatService:
    def __init__(self, ai_provider: AIProvider = OpenAIProvider(), voice_service: VoiceService = None):
        self.ai_provider = ai_provider
        self.voice_service = voice_service or VoiceService()

    def create_conversation(self, db: Session, user_id: int, title: Optional[str] = None) -> ConversationModel:
        if not title:
            title = "New Conversation"
        conversation = conversation_crud.create(db, obj_in=ConversationCreate(user_id=user_id, title=title))
        return conversation

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

    async def send_streaming_message(self, messages: List[Message], db: Session, agent_type: str, conversation_id: int, user_id: int) -> Iterator[str]: # type: ignore
        latest_user_message = messages[-1].content if messages and messages[-1].role == "user" else ""
        context = self._retrieve_context(latest_user_message, db)

        if agent_type == "innovative":
            system_prompt = prompt_templates.INNOVATIVE_AGENT_SYSTEM_PROMPT.format(context=context)
        elif agent_type == "compliance":
            system_prompt = prompt_templates.COMPLIANCE_AGENT_SYSTEM_PROMPT.format(context=context)
        else:
            system_prompt = prompt_templates.DEFAULT_AGENT_SYSTEM_PROMPT.format(context=context)

        history_from_db = chat_message_crud.get_by_conversation_id(db, conversation_id=conversation_id)

        valid_chat_roles = {'user', 'assistant'}
        historical_messages = [
            Message(role=msg.role if msg.role in valid_chat_roles else 'user', content=msg.content)
            for msg in history_from_db
        ]

        messages_for_ai = [Message(role="system", content=system_prompt)] + historical_messages + messages

        for message in messages:
            chat_message_crud.create(db, obj_in=ChatMessageCreate(conversation_id=conversation_id, role=message.role, content=message.content))

        full_ai_response_content = []

        async for chunk in self.ai_provider.generate_chat_completion(messages_for_ai):
            full_ai_response_content.append(chunk)
            yield chunk

        ai_response_content = "".join(full_ai_response_content)
        chat_message_crud.create(db, obj_in=ChatMessageCreate(conversation_id=conversation_id, role="assistant", content=ai_response_content))

    def get_user_conversations(self, db: Session, user_id: int) -> List[ConversationModel]:
        return conversation_crud.get_by_user_id_sorted(db, user_id=user_id)

    def validate_conversation_access(self, db: Session, conversation_id: int, user_id: int) -> ConversationModel:
        """Validate that conversation exists and user has access."""
        if conversation_id <= 0:
            raise ValueError("Invalid conversation_id")

        conversation = db.query(ConversationModel).filter(
            ConversationModel.id == conversation_id,
            ConversationModel.user_id == user_id
        ).first()

        if not conversation:
            raise ValueError("Conversation not found or access denied")

        return conversation

    async def process_audio_input(self, audio_file: UploadFile) -> List[Message]:
        """Process audio file input and return text messages."""
        if not self.voice_service.validate_audio_file(audio_file):
            raise ValueError("Invalid audio file. Supported formats: WAV, MP3, MP4, WebM, OGG, FLAC. Max size: 25MB.")

        transcribed_text = await self.voice_service.transcribe_audio(audio_file)

        if not transcribed_text or not transcribed_text.strip():
            raise ValueError("Could not transcribe audio or audio was empty")

        return [Message(role="user", content=transcribed_text)]

    def process_text_input(self, message: str) -> List[Message]:
        """Process plain text input and return messages."""
        if not message or not message.strip():
            raise ValueError("Message cannot be empty")

        return [Message(role="user", content=message.strip())]

    def validate_chat_input(self, message: Optional[str], audio_file: Optional[UploadFile],
                          agent_type: str) -> None:
        """Validate chat input parameters."""
        has_message = message is not None and message.strip()
        has_audio = audio_file is not None

        if not has_message and not has_audio:
            raise ValueError("Either 'message' or 'audio_file' must be provided")

        ALLOWED_AGENT_TYPES = {"innovative", "compliance", "default"}
        if agent_type not in ALLOWED_AGENT_TYPES:
            raise ValueError(f"Invalid agent_type. Must be one of: {', '.join(ALLOWED_AGENT_TYPES)}")

    async def validate_and_process_input(self, message: Optional[str], audio_file: Optional[UploadFile],
                                       agent_type: str, conversation_id: int, user_id: int, db: Session) -> tuple:
        """Validate input and return processed messages and conversation."""
        self.validate_chat_input(message, audio_file, agent_type)

        conversation = self.validate_conversation_access(db, conversation_id, user_id)

        if audio_file:
            processed_messages = await self.process_audio_input(audio_file)
        elif message:
            processed_messages = self.process_text_input(message)
        else:
            raise ValueError("No valid input provided")

        return processed_messages, conversation
