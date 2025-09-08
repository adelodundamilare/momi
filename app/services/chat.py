from typing import List, Iterator
import openai
from app.core.config import settings
from app.schemas.chat import Message

class ChatService:
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

    def send_streaming_message(self, messages: List[Message]) -> Iterator[str]:
        """
        Calls the OpenAI API in streaming mode and yields the content chunks.
        """
        message_dicts = [msg.dict() for msg in messages]

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
