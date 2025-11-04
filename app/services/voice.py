import tempfile
import logging
from fastapi import UploadFile
from openai import OpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)

class VoiceService:
    """Service for handling voice/audio processing using OpenAI Whisper."""

    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    async def transcribe_audio(self, audio_file: UploadFile) -> str:
        """
        Transcribe audio file to text using OpenAI Whisper.

        Args:
            audio_file: Uploaded audio file

        Returns:
            str: Transcribed text

        Raises:
            Exception: If transcription fails
        """
        try:
            audio_bytes = await audio_file.read()

            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(audio_bytes)
                temp_file.flush()

                with open(temp_file.name, "rb") as audio:
                    transcript = self.client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio,
                        language="en",
                        response_format="text"
                    )

            logger.info(f"Successfully transcribed audio file: {audio_file.filename}")
            return transcript

        except Exception as e:
            logger.error(f"Failed to transcribe audio file {audio_file.filename}: {str(e)}")
            raise Exception(f"Audio transcription failed: {str(e)}")

    def validate_audio_file(self, audio_file: UploadFile) -> bool:
        """
        Validate that the uploaded file is a supported audio format.

        Args:
            audio_file: Uploaded file to validate

        Returns:
            bool: True if valid audio file
        """
        supported_formats = [
            'audio/wav', 'audio/mpeg', 'audio/mp3', 'audio/mp4',
            'audio/webm', 'audio/ogg', 'audio/flac'
        ]

        content_type = audio_file.content_type
        if content_type not in supported_formats:
            logger.warning(f"Unsupported audio format: {content_type}")
            return False

        if hasattr(audio_file, 'size') and audio_file.size > 25 * 1024 * 1024:
            logger.warning(f"Audio file too large: {audio_file.size} bytes")
            return False

        return True
