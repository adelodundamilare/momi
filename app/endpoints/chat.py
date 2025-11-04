from fastapi import APIRouter, Depends, HTTPException, status, Form, File, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.schemas.chat import ChatRequest, Message
from app.services.chat import ChatService
from app.services.voice import VoiceService
from app.utils.deps import get_current_user
from app.models.user import User
from app.schemas.utility import APIResponse
from app.utils.logger import setup_logger
from app.schemas.conversation import Conversation as ConversationSchema, ConversationCreateRequest

logger = setup_logger("chat_api", "chat.log")

router = APIRouter()

chat_service = ChatService()
voice_service = VoiceService()

@router.post("/conversations/", response_model=ConversationSchema)
def create_conversation(
    request: ConversationCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new conversation.
    """
    try:
        conversation = chat_service.create_conversation(db, user_id=current_user.id, title=request.title)
        return conversation
    except Exception as e:
        logger.error(f"Error in create_conversation: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/")
async def stream_chat(
    message: Optional[str] = Form(None, description="Text message content"),
    audio_file: Optional[UploadFile] = File(None, description="Audio file for voice input"),
    agent_type: str = Form("innovative", description="Type of AI agent to use"),
    conversation_id: int = Form(..., description="Conversation ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        processed_messages, conversation = await chat_service.validate_and_process_input(
            message, audio_file, agent_type, conversation_id, current_user.id, db
        )

        return StreamingResponse(
            chat_service.send_streaming_message(
                processed_messages, db, agent_type, conversation_id, current_user.id
            ),
            media_type="text/event-stream"
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in stream_chat: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred"
        )
    finally:
        if audio_file:
            await audio_file.close()

@router.get("/history", response_model=APIResponse)
def get_chat_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve chat history for the current user.
    """
    try:
        conversations = chat_service.get_user_conversations(db, current_user.id)
        conversations_response = [ConversationSchema.from_orm(c) for c in conversations]
        return APIResponse(message="Chat history retrieved successfully", data=conversations_response)
    except Exception as e:
        logger.error(f"Error in get_chat_history: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
