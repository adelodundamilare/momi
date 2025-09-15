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
    AITrendSignals,
    AIIngredientEnrichment,
    AIInsightPortalData,
    AIFormulaDetails
)
from app.schemas.marketing import AIMarketingCopy
from app.utils import prompt_templates

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

    @abstractmethod
    async def generate_marketing_copy(self, formula_name: str, formula_description: str) -> AIMarketingCopy:
        pass

    @abstractmethod
    async def generate_image(self, prompt: str) -> str:
        pass

    @abstractmethod
    async def categorize_product(self, product_name: str, product_description: str) -> str:
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
        system_prompt = self._create_prompt_from_model(AISummaryAndSentiment, prompt_templates.SUMMARY_AND_SENTIMENT_INSTRUCTION)
        return await self._make_ai_call(system_prompt, text_content, AISummaryAndSentiment)

    async def generate_trend_signals(self, combined_content: str) -> AITrendSignals:
        system_prompt = self._create_prompt_from_model(AITrendSignals, prompt_templates.TREND_SIGNALS_INSTRUCTION)
        return await self._make_ai_call(system_prompt, combined_content, AITrendSignals)

    async def generate_ingredient_enrichment(self, ingredient_name: str) -> AIIngredientEnrichment:
        instruction = prompt_templates.INGREDIENT_ENRICHMENT_INSTRUCTION.format(ingredient_name=ingredient_name)
        system_prompt = self._create_prompt_from_model(AIIngredientEnrichment, instruction)
        user_prompt = f"Generate enrichment data for {ingredient_name}."
        return await self._make_ai_call(system_prompt, user_prompt, AIIngredientEnrichment)

    async def generate_insight_portal_data(self, ingredient_name: str) -> AIInsightPortalData:
        instruction = prompt_templates.INSIGHT_PORTAL_INSTRUCTION.format(ingredient_name=ingredient_name)
        system_prompt = self._create_prompt_from_model(AIInsightPortalData, instruction)
        user_prompt = f"Generate insight portal data for {ingredient_name}."
        return await self._make_ai_call(system_prompt, user_prompt, AIInsightPortalData)

    async def generate_formula_details(self, product_concept: str) -> AIFormulaDetails:
        system_prompt = self._create_prompt_from_model(AIFormulaDetails, prompt_templates.FORMULA_DETAILS_INSTRUCTION)
        user_prompt = f"The product concept is: {product_concept}"
        return await self._make_ai_call(system_prompt, user_prompt, AIFormulaDetails)

    async def generate_marketing_copy(self, formula_name: str, formula_description: str) -> AIMarketingCopy:
        system_prompt = self._create_prompt_from_model(AIMarketingCopy, prompt_templates.MARKETING_COPY_INSTRUCTION)
        user_prompt = f"Formula Name: {formula_name}\nFormula Description: {formula_description}"
        return await self._make_ai_call(system_prompt, user_prompt, AIMarketingCopy)

    async def generate_image(self, prompt: str) -> str:
        """Generates an image using DALL-E 3 and returns the URL."""
        try:
            response = await self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                n=1,
                size="1024x1024",
                quality="standard",
                response_format="url"
            )
            return response.data[0].url
        except openai.APIError as e:
            logger.error(f"OpenAI DALL-E error: {e}")
            raise AIProviderError("Failed to generate image.") from e

    async def categorize_product(self, product_name: str, product_description: str) -> str:
        """Categorizes the product into one of several predefined categories."""
        system_prompt = prompt_templates.PRODUCT_CATEGORIZATION_SYSTEM_PROMPT
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Product Name: {product_name}\nDescription: {product_description}"}
                ],
                temperature=0,
            )
            return response.choices[0].message.content.strip("'.\" ")
        except Exception as e:
            logger.error(f"An unexpected error occurred during product categorization: {e}")
            # Fallback to a generic category
            return "Other"
