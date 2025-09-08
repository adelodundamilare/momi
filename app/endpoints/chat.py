from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.schemas.chat import ChatRequest
from app.services.chat import ChatService

router = APIRouter()

# It's better to instantiate the service once
chat_service = ChatService()

@router.post("/")
def stream_chat(
    request: ChatRequest
):
    """
    Receives a chat history and streams back a response from the AI.
    """
    return StreamingResponse(
        chat_service.send_streaming_message(request.messages), 
        media_type="text/event-stream"
    )
