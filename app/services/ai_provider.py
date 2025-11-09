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
    AICommercializationInsights,
    AICostAnalysisOutput,
    AISummaryAndSentiment,
    AISupplierAnalysisOutput,
    AITrendSignals,
    AIIngredientEnrichment,
    AIInsightPortalData,
    AIFormulaDetails,
    AITrendData,AITrendCategoryAndTags
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
    async def generate_insight_portal_data_with_context(self, ingredient_name: str, chat_context: str) -> AIInsightPortalData:
        pass

    @abstractmethod
    async def generate_formula_details(self, product_concept: str, market_insights: Optional[Dict[str, Any]] = None) -> AIFormulaDetails:
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

    @abstractmethod
    async def extract_trend_data(self, article_title: str, article_content: str) -> AITrendData:
        pass

    @abstractmethod
    async def generate_supplier_analysis(self, workflow_request_data: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def generate_cost_analysis(self, workflow_request_data: Dict[str, Any]) -> Dict[str, Any]:
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
            raise AIProviderError(f"AI response failed validation for {response_model.__name__}.") from e
        except openai.APIError as e:
            logger.warning(f"OpenAI API error on attempt: {e}. Retrying...")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred in the AI call: {e}")
            raise AIProviderError("An unexpected error occurred.") from e

    async def generate_chat_completion(self, messages: List[Message]) -> Iterator[str]: # type: ignore
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

    async def generate_insight_portal_data_with_context(self, ingredient_name: str, chat_context: str) -> AIInsightPortalData:
        """Generate insight portal data with personalized chat context."""
        contextual_instruction = f"""
You are an AI assistant specializing in food and beverage market analysis.

USER CONVERSATION CONTEXT:
{chat_context}

TASK:
1. Analyze the entire conversation and identify ALL food ingredients mentioned
2. From those ingredients, select the SINGLE most relevant/important one as the focus
3. Generate insights primarily for that top ingredient

INGREDIENT EXTRACTION RULES:
- Look for actual food ingredients (rice, tomatoes, peppers, stock, spices, etc.)
- Include cooking ingredients, vegetables, proteins, seasonings, etc.
- Consider context clues about what the user is researching
- Extract specific ingredient names from recipes, discussions, questions

REQUIREMENTS:
- If NO ingredients are clearly mentioned, return error about insufficient context
- If ingredients ARE mentioned, always select one as the top focus
- Use multi-ingredient context to provide richer insights
- Do NOT provide generic insights or make assumptions
- Do NOT analyze "General Ingredient" or similar fallbacks

If context is insufficient, return a complete response with: {{"error": "insufficient_context", "error_message": "Unable to determine specific ingredient from conversation. Please provide more specific details about which ingredient you want market insights for.", "identified_ingredient": null, "shared_product_concepts": [], "company_competitors": [], "assistant_recommendations": {{"opportunity": "", "risk": ""}}, "demography_data": {{}}, "gender_bias": {{"male": 0, "female": 0}}, "top_geographic_locations": []}}

Focus your analysis on the ingredients, trends, and topics they've been exploring in their conversation. Make the insights actionable and directly relevant to their apparent interests and needs.
"""
        system_prompt = self._create_prompt_from_model(AIInsightPortalData, contextual_instruction)
        user_prompt = f"Analyze the conversation context and generate market insights for the most relevant ingredient discussed."
        return await self._make_ai_call(system_prompt, user_prompt, AIInsightPortalData)

    async def generate_formula_details(self, product_concept: str, market_insights: Optional[Dict[str, Any]] = None) -> AIFormulaDetails:
        if market_insights:
            enhanced_instruction = f"""
{prompt_templates.FORMULA_DETAILS_INSTRUCTION}

MARKET CONTEXT:
- Trending product concepts: {', '.join([str(c.get('title', '')) for c in market_insights.get('shared_product_concepts', [])])}
- Key competitors: {', '.join(market_insights.get('company_competitors', []))}
- Market opportunities: {market_insights.get('assistant_recommendations', {}).get('opportunity', '')}
- Target demographics: {', '.join([f"{k}: {v}" for k, v in market_insights.get('demography_data', {}).items()])}
- Geographic focus: {', '.join(market_insights.get('top_geographic_locations', []))}

Create a formula that leverages current market trends and addresses identified opportunities.
"""
            system_prompt = self._create_prompt_from_model(AIFormulaDetails, enhanced_instruction)
            user_prompt = f"Create a market-driven formula for: {product_concept}"
        else:
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
            return "Other"

    async def extract_trend_data(self, article_title: str, article_content: str) -> AITrendData:
        instruction = prompt_templates.TREND_DATA_EXTRACTION_INSTRUCTION
        system_prompt = self._create_prompt_from_model(AITrendData, instruction)
        user_prompt = f"Article Title: {article_title}\nArticle Content: {article_content}"
        return await self._make_ai_call(system_prompt, user_prompt, AITrendData)

    async def generate_trend_category_and_tags(self, article_title: str, article_content: str) -> AITrendCategoryAndTags:
        instruction = prompt_templates.TREND_CATEGORY_AND_TAGS_INSTRUCTION
        system_prompt = self._create_prompt_from_model(AITrendCategoryAndTags, instruction)
        user_prompt = f"Article Title: {article_title}\nArticle Content: {article_content}"
        return await self._make_ai_call(system_prompt, user_prompt, AITrendCategoryAndTags)

    async def generate_commercialization_insights(
        self,
        formula_name: str,
        formula_description: str,
        master_tasks_data: List[Dict[str, Any]]
    ) -> AICommercializationInsights:
        instruction = prompt_templates.COMMERCIALIZATION_INSIGHTS_INSTRUCTION
        system_prompt = self._create_prompt_from_model(AICommercializationInsights, instruction)

        user_prompt = (
            f"Analyze the following commercialization workflow for a product.\n\n"
            f"Product: {formula_name}\n"
            f"Description: {formula_description}\n\n"
            f"Defined Tasks (predict durations for these): {json.dumps(master_tasks_data, indent=2)}\n\n"
            "Based on this information, predict accurate durations for each task, identify all potential risks, and generate comprehensive recommendations to optimize the workflow, reduce risks, and improve the timeline. Focus on actionable insights."
        )
        return await self._make_ai_call(system_prompt, user_prompt, AICommercializationInsights)

    async def generate_supplier_analysis(self, workflow_request_data: Dict[str, Any]) -> AISupplierAnalysisOutput:
        instruction = prompt_templates.SUPPLIER_ANALYSIS_INSTRUCTION
        system_prompt = self._create_prompt_from_model(AISupplierAnalysisOutput, instruction)
        user_prompt = f"Analyze suppliers for the following workflow request: {json.dumps(workflow_request_data, indent=2)}"
        return await self._make_ai_call(system_prompt, user_prompt, AISupplierAnalysisOutput)

    async def generate_cost_analysis(self, workflow_request_data: Dict[str, Any]) -> AICostAnalysisOutput:
        instruction = prompt_templates.COST_ANALYSIS_INSTRUCTION
        system_prompt = self._create_prompt_from_model(AICostAnalysisOutput, instruction)
        user_prompt = f"Calculate costs for the following workflow request: {json.dumps(workflow_request_data, indent=2)}"
        return await self._make_ai_call(system_prompt, user_prompt, AICostAnalysisOutput)
