from abc import ABC, abstractmethod
from typing import List, Iterator, Dict, Any
import openai
import json

from app.core.config import settings
from app.schemas.chat import Message

class AIProvider(ABC):
    @abstractmethod
    def generate_chat_completion(self, messages: List[Message]) -> Iterator[str]:
        pass

    @abstractmethod
    def generate_summary_and_sentiment(self, text_content: str) -> Dict[str, str]:
        pass

    @abstractmethod
    def generate_ingredient_substitutions(self, ingredient_name: str) -> List[str]:
        pass

    @abstractmethod
    def generate_trend_signals(self, combined_content: str) -> List[str]:
        pass

    @abstractmethod
    def generate_ingredient_enrichment(self, ingredient_name: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def generate_insight_portal_data(self, ingredient_name: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def generate_formula_details(self, product_concept: str) -> Dict[str, Any]:
        pass

class OpenAIProvider(AIProvider):
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4-turbo" # Default model for JSON mode

    def generate_chat_completion(self, messages: List[Message]) -> Iterator[str]:
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

    def generate_summary_and_sentiment(self, text_content: str) -> Dict[str, str]:
        system_prompt = (
            "You are an expert analyst. Analyze the following article and provide a concise, "
            "one-paragraph summary and a sentiment analysis (either Positive, Negative, or Neutral). "
            "Respond with a JSON object containing two keys: 'summary' and 'sentiment'."
        )
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text_content}
                ]
            )
            insights = json.loads(response.choices[0].message.content)
            return {
                "summary": insights.get("summary", "No summary generated."),
                "sentiment": insights.get("sentiment", "No sentiment generated.")
            }
        except Exception as e:
            print(f"Error generating summary/sentiment: {e}")
            return {"summary": "Error", "sentiment": "Error"}

    def generate_ingredient_substitutions(self, ingredient_name: str) -> List[str]:
        system_prompt = (
            "You are an expert in food and beverage ingredient science. "
            "For the given ingredient, suggest 3-5 common and functionally similar alternatives "
            "that could be used in food and beverage products. "
            "Respond with a JSON array of strings, where each string is an alternative ingredient name."
        )
        user_prompt = f"Suggest alternatives for: {ingredient_name}"
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            response_content = json.loads(response.choices[0].message.content)
            alternatives = response_content.get("alternatives", [])
            return alternatives if isinstance(alternatives, list) else []
        except Exception as e:
            print(f"Error suggesting substitutions for {ingredient_name}: {e}")
            return []

    def generate_trend_signals(self, combined_content: str) -> List[str]:
        system_prompt = (
            """You are an expert in food and beverage market trends. Analyze the following social media posts
            and identify clear trend signals. A trend signal is a specific ingredient, product type, or concept
            that is showing a clear upward (^) or downward (v) trend.
            Respond with a JSON array of strings, where each string is a trend signal in the format '[Item] [^/v]'.
            Example: ['Moringa ^', 'Spirulina v', 'Kombucha ^']."""
        )
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": combined_content}
                ]
            )
            response_content = json.loads(response.choices[0].message.content)
            signals = response_content.get("signals", [])
            return signals if isinstance(signals, list) else []
        except Exception as e:
            print(f"An error occurred while generating trend signals: {e}")
            return []

    def generate_ingredient_enrichment(self, ingredient_name: str) -> Dict[str, Any]:
        def _call_ai_for_json(system_prompt: str, user_prompt: str) -> Dict[str, Any]:
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    response_format={"type": "json_object"},
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ]
                )
                return json.loads(response.choices[0].message.content)
            except Exception as e:
                print(f"Error in AI call for enrichment: {e}")
                return {}

        # 1. Description
        description_prompt = (
            f"You are an expert in food and beverage ingredients. For the ingredient '{ingredient_name}', generate a concise description. "
            f"Respond with a JSON object with key: 'description'."
        )
        description_data = _call_ai_for_json(description_prompt, f"Description for {ingredient_name}")

        # 2. Benefits
        benefits_prompt = (
            f"You are an expert in food and beverage ingredients. For the ingredient '{ingredient_name}', generate 3-5 key benefits (as a single string). "
            f"Respond with a JSON object with key: 'benefits'."
        )
        benefits_data = _call_ai_for_json(benefits_prompt, f"Benefits for {ingredient_name}")

        # 3. Claims
        claims_prompt = (
            f"You are an expert in food and beverage ingredients. For the ingredient '{ingredient_name}', generate 2-3 common claims (as a single string). "
            f"Respond with a JSON object with key: 'claims'."
        )
        claims_data = _call_ai_for_json(claims_prompt, f"Claims for {ingredient_name}")

        # 4. Regulatory Notes
        regulatory_notes_prompt = (
            f"You are an expert in food and beverage ingredients. For the ingredient '{ingredient_name}', generate 1-2 regulatory notes (as a single string). "
            f"Respond with a JSON object with key: 'regulatory_notes'."
        )
        regulatory_notes_data = _call_ai_for_json(regulatory_notes_prompt, f"Regulatory notes for {ingredient_name}")

        # 5. Function
        function_prompt = (
            f"You are an expert in food and beverage ingredients. For the ingredient '{ingredient_name}', generate its primary function in food products (as a single string). "
            f"Respond with a JSON object with key: 'function'."
        )
        function_data = _call_ai_for_json(function_prompt, f"Function for {ingredient_name}")

        # 6. Weight, Unit, Cost, Allergies
        misc_data_prompt = (
            f"You are an expert in food and beverage ingredients. For the ingredient '{ingredient_name}', generate: "
            f"- an estimated typical weight (e.g., 100)\n"
            f"- unit (e.g., 'grams', 'ml', 'pieces')\n"
            f"- common allergies associated with it (as a comma-separated string).\n"
            f"Respond with a JSON object with keys: 'weight', 'unit', 'allergies'."
        )
        misc_data = _call_ai_for_json(misc_data_prompt, f"Misc data for {ingredient_name}")

        return {
            "description": description_data.get("description"),
            "benefits": benefits_data.get("benefits"),
            "claims": claims_data.get("claims"),
            "regulatory_notes": regulatory_notes_data.get("regulatory_notes"),
            "function": function_data.get("function"),
            "weight": misc_data.get("weight"),
            "unit": misc_data.get("unit"),
            "allergies": misc_data.get("allergies"),
        }

    def generate_insight_portal_data(self, ingredient_name: str) -> Dict[str, Any]:
        # Helper function for making AI calls with specific prompts
        def _call_ai_for_json(system_prompt: str, user_prompt: str) -> Dict[str, Any]:
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    response_format={"type": "json_object"},
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ]
                )
                return json.loads(response.choices[0].message.content)
            except Exception as e:
                print(f"Error in AI call: {e}")
                return {}

        # 1. Shared Product Concepts
        product_concept_prompt = (
            f"You are an AI assistant specializing in food and beverage product development. "
            f"For the ingredient '{ingredient_name}', generate 3-5 innovative product concepts. "
            f"For each concept, provide a title, a plausible URL for a product concept image, and a list of 3-5 key ingredients (including '{ingredient_name}' if applicable). "
            f"Respond with a JSON object where 'shared_product_concepts' is a list of objects, each with 'image' (string URL, e.g., 'https://example.com/image.jpg'), 'title' (string), and 'key_ingredients' (list of strings, e.g., ['Ingredient A', 'Ingredient B'])."
        )
        product_concept_data = _call_ai_for_json(product_concept_prompt, f"Product concepts for {ingredient_name}")

        # 2. Company Competitors
        competitors_prompt = (
            f"You are an AI assistant specializing in food and beverage market analysis. "
            f"For products featuring '{ingredient_name}', identify 3-5 potential competitor companies or brands. "
            f"Respond with a JSON object where 'company_competitors' is a list of strings."
        )
        competitors_data = _call_ai_for_json(competitors_prompt, f"Competitors for {ingredient_name}")

        # 3. Assistant Recommendations
        recommendations_prompt = (
            f"You are an AI assistant providing strategic recommendations for food and beverage businesses. "
            f"For the ingredient '{ingredient_name}', provide one key opportunity and one key risk for product development or market strategy. "
            f"Respond with a JSON object where 'assistant_recommendations' is an object with 'opportunity' (string) and 'risk' (string) keys."
        )
        recommendations_data = _call_ai_for_json(recommendations_prompt, f"Recommendations for {ingredient_name}")

        # 4. Demography Data
        demography_prompt = (
            f"You are an AI assistant specializing in consumer demographics for food and beverage. "
            f"For products featuring '{ingredient_name}', generate plausible demographic data for age groups (18-24, 25-34, 35-44, 45-54, 55-64, 65+). "
            f"Respond with a JSON object where 'demography_data' is a dictionary with age ranges as keys and integer counts as values."
        )
        demography_data = _call_ai_for_json(demography_prompt, f"Demography data for {ingredient_name}")

        # 5. Gender Bias
        gender_bias_prompt = (
            f"You are an AI assistant specializing in consumer demographics for food and beverage. "
            f"For products featuring '{ingredient_name}', generate plausible gender bias data (male vs female ratio). "
            f"Respond with a JSON object where 'gender_bias' is a dictionary with 'male' and 'female' as keys and float ratios as values (summing to 1.0)."
        )
        gender_bias_data = _call_ai_for_json(gender_bias_prompt, f"Gender bias for {ingredient_name}")

        # 6. Top Geographic Locations
        geo_prompt = (
            f"You are an AI assistant specializing in food and beverage market geography. "
            f"For products featuring '{ingredient_name}', identify 3-5 top plausible geographic locations for consumption or market interest. "
            f"Respond with a JSON object where 'top_geographic_locations' is a list of strings."
        )
        geo_data = _call_ai_for_json(geo_prompt, f"Top geographic locations for {ingredient_name}")

        # Aggregate results
        final_data = {
            "shared_product_concepts": product_concept_data.get("shared_product_concepts", []),
            "key_ingredients": product_concept_data.get("key_ingredients", []),
            "product_concept_image": product_concept_data.get("product_concept_image"),
            "company_competitors": competitors_data.get("company_competitors", []),
            "assistant_recommendations": recommendations_data.get("assistant_recommendations", {}),
            "demography_data": demography_data.get("demography_data", {}),
            "gender_bias": gender_bias_data.get("gender_bias", {}),
            "top_geographic_locations": geo_data.get("top_geographic_locations", []),
        }

        # Ensure demography_data values are integers
        if "demography_data" in final_data and isinstance(final_data["demography_data"], dict):
            final_data["demography_data"] = {k: int(v) for k, v in final_data["demography_data"].items()}

        return final_data

    def generate_formula_details(self, product_concept: str) -> Dict[str, Any]:
        system_prompt = (
            f"You are an AI assistant specializing in food and beverage formula development. "
            f"For the product concept '{product_concept}', generate a plausible formula including: "
            f"- A formula name (string)\n"
            f"- A formula description (string)\n"
            f"- A list of 5-10 key ingredients, each with:\n"
            f"    - name (string)\n"
            f"    - quantity (float)\n"
            f"    - estimated_cost (float)\n"
            f"Respond with a JSON object with keys: 'formula_name', 'formula_description', 'ingredients' (list of objects)."
        )
        user_prompt = f"Generate formula details for: {product_concept}"
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            response_content = json.loads(response.choices[0].message.content)
            return response_content
        except Exception as e:
            print(f"Error generating formula details for {product_concept}: {e}")
            return {}
