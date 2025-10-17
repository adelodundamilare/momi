from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.chat import ChatRequest
from app.services.chat import ChatService
from app.utils.deps import get_current_user
from app.models.user import User
from app.schemas.utility import APIResponse
from app.utils.logger import setup_logger
from app.schemas.conversation import Conversation, ConversationCreateRequest

logger = setup_logger("chat_api", "chat.log")

router = APIRouter()

chat_service = ChatService()

@router.post("/conversations/", response_model=Conversation)
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
def stream_chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        if request.conversation_id == 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="conversation_id cannot be 0")
        return StreamingResponse(
            chat_service.send_streaming_message(request.messages, db, request.agent_type, request.conversation_id, current_user.id),
            media_type="text/event-stream"
        )
    except Exception as e:
        logger.error(f"Error in stream_chat: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

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
        conversations_response = [Conversation.from_orm(c) for c in conversations]
        return APIResponse(message="Chat history retrieved successfully", data=conversations_response)
    except Exception as e:
        logger.error(f"Error in get_chat_history: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))