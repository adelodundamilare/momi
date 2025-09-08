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
