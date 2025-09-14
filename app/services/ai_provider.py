from abc import ABC, abstractmethod
from typing import List, Iterator, Dict, Any, Type, Optional
import openai
import json
import logging
from pydantic import BaseModel, ValidationError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.core.config import settings
from app.schemas.chat import Message
from app.schemas.ai_responses import (
    AISummaryAndSentiment,
    AIIngredientSubstitutions,
    AITrendSignals,
    AIIngredientEnrichment,
    AIInsightPortalData,
    AIFormulaDetails
)

# Setup logger
logger = logging.getLogger(__name__)

# Custom Exception for the provider
class AIProviderError(Exception):
    """Custom exception for AI Provider failures."""
    pass

class AIProvider(ABC):
    # ... (Abstract methods remain the same)
    @abstractmethod
    async def generate_chat_completion(self, messages: List[Message]) -> Iterator[str]:
        pass

    @abstractmethod
    async def generate_summary_and_sentiment(self, text_content: str) -> AISummaryAndSentiment:
        pass

    @abstractmethod
    async def generate_ingredient_substitutions(self, ingredient_name: str) -> AIIngredientSubstitutions:
        pass

    @abstractmethod
    async def generate_trend_signals(self, combined_content: str) -> AITrendSignals:
        pass

    @abstractmethod
    async def generate_ingredient_enrichment(self, ingredient_name: str) -> AIIngredientEnrichment:
        pass

    @abstractmethod
    async def generate_insight_portal_data(self, ingredient_name: str) -> AIInsightPortalData:
        pass

    @abstractmethod
    async def generate_formula_details(self, product_concept: str) -> AIFormulaDetails:
        pass

class OpenAIProvider(AIProvider):
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4-turbo"

    def _create_prompt_from_model(self, model_class: Type[BaseModel], instruction: str) -> str:
        schema = model_class.model_json_schema()
        schema_str = json.dumps(schema, indent=2)
        return (
            f"{instruction}\n\n"
            "Your response MUST be a single JSON object that strictly adheres to the following JSON Schema.\n\n"
            "### JSON Schema\n"
            f"{schema_str}"
        )

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(openai.APIError),
        reraise=True  # Reraise the exception after the final attempt
    )
    async def _make_ai_call(
        self,
        system_prompt: str,
        user_prompt: str,
        response_model: Type[BaseModel]
    ) -> BaseModel:
        """Helper function to make a structured, validated, and resilient call to the OpenAI API."""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            response_json = json.loads(response.choices[0].message.content)
            return response_model.model_validate(response_json)
        except ValidationError as e:
            logger.error(f"Pydantic validation error for {response_model.__name__}: {e}")
            # Do not retry on validation error, it's a permanent failure for this response.
            raise AIProviderError(f"AI response failed validation for {response_model.__name__}.") from e
        except openai.APIError as e:
            logger.warning(f"OpenAI API error on attempt: {e}. Retrying...")
            raise  # Reraise the exception to trigger tenacity retry
        except Exception as e:
            logger.error(f"An unexpected error occurred in the AI call: {e}")
            raise AIProviderError("An unexpected error occurred.") from e

    async def generate_chat_completion(self, messages: List[Message]) -> Iterator[str]:
        # Chat completion is not retried in the same way, as it's a stream.
        message_dicts = [msg.dict() for msg in messages]
        try:
            stream = await self.client.chat.completions.create(
                model="gpt-4",
                messages=message_dicts,
                stream=True,
            )
            async for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
        except Exception as e:
            logger.error(f"OpenAI API stream error: {e}")
            yield "Error: Could not connect to the AI service."

    async def generate_summary_and_sentiment(self, text_content: str) -> AISummaryAndSentiment:
        instruction = "You are an expert analyst. Analyze the provided article and provide a concise, one-paragraph summary and a sentiment analysis (Positive, Negative, or Neutral)."
        system_prompt = self._create_prompt_from_model(AISummaryAndSentiment, instruction)
        return await self._make_ai_call(system_prompt, text_content, AISummaryAndSentiment)

    async def generate_ingredient_substitutions(self, ingredient_name: str) -> AIIngredientSubstitutions:
        instruction = "You are an expert in food ingredient science. For the given ingredient, suggest 3-5 common and functionally similar alternatives."
        system_prompt = self._create_prompt_from_model(AIIngredientSubstitutions, instruction)
        user_prompt = f"The ingredient is: {ingredient_name}"
        return await self._make_ai_call(system_prompt, user_prompt, AIIngredientSubstitutions)

    async def generate_trend_signals(self, combined_content: str) -> AITrendSignals:
        instruction = "You are an expert in food market trends. Analyze the provided social media posts and identify trend signals. A trend signal is an ingredient, product, or concept with an upward (^) or downward (v) trend."
        system_prompt = self._create_prompt_from_model(AITrendSignals, instruction)
        return await self._make_ai_call(system_prompt, combined_content, AITrendSignals)

    async def generate_ingredient_enrichment(self, ingredient_name: str) -> AIIngredientEnrichment:
        instruction = f"You are an expert in food ingredients. For the ingredient '{ingredient_name}', provide a detailed enrichment covering its description, benefits, common claims, regulatory notes, function, and typical allergies."
        system_prompt = self._create_prompt_from_model(AIIngredientEnrichment, instruction)
        user_prompt = f"Generate enrichment data for {ingredient_name}."
        return await self._make_ai_call(system_prompt, user_prompt, AIIngredientEnrichment)

    async def generate_insight_portal_data(self, ingredient_name: str) -> AIInsightPortalData:
        instruction = f"You are an AI assistant specializing in food and beverage market analysis. For the ingredient '{ingredient_name}', generate a comprehensive market insight report."
        system_prompt = self._create_prompt_from_model(AIInsightPortalData, instruction)
        user_prompt = f"Generate insight portal data for {ingredient_name}."
        return await self._make_ai_call(system_prompt, user_prompt, AIInsightPortalData)

    async def generate_formula_details(self, product_concept: str) -> AIFormulaDetails:
        instruction = f"You are an AI assistant for food and beverage formula development. For the given product concept, generate a plausible formula."
        system_prompt = self._create_prompt_from_model(AIFormulaDetails, instruction)
        user_prompt = f"The product concept is: {product_concept}"
        return await self._make_ai_call(system_prompt, user_prompt, AIFormulaDetails)
