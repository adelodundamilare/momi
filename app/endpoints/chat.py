from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.chat import ChatRequest
from app.services.chat import ChatService

router = APIRouter()

# It's better to instantiate the service once
chat_service = ChatService()

@router.post("/")
def stream_chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    Receives a chat history and streams back a response from the AI.
    """
    return StreamingResponse(
        chat_service.send_streaming_message(request.messages, db), 
        media_type="text/event-stream"
    )
