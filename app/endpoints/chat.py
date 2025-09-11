from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.chat import ChatRequest, ChatHistory, ChatHistoryCreate
from app.services.chat import ChatService
from app.crud.chat import chat_history
from app.utils.deps import get_current_user
from app.models.user import User
from app.schemas.utility import APIResponse

router = APIRouter()

# It's better to instantiate the service once
chat_service = ChatService()

@router.post("/")
def stream_chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Receives a chat history and streams back a response from the AI.
    """
    chat_history.create(db, obj_in=ChatHistoryCreate(user_id=current_user.id, messages=request.messages))
    return StreamingResponse(
        chat_service.send_streaming_message(request.messages, db, request.agent_type), 
        media_type="text/event-stream"
    )

@router.get("/history", response_model=APIResponse)
def get_chat_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve chat history for the current user.
    """
    history = db.query(ChatHistory).filter(ChatHistory.user_id == current_user.id).all()
    return APIResponse(message="Chat history retrieved successfully", data=history)

@router.post("/save", response_model=APIResponse)
def save_chat_history(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Save a chat history.
    """
    chat_history.create(db, obj_in=ChatHistoryCreate(user_id=current_user.id, messages=request.messages))
    return APIResponse(message="Chat history saved successfully")
