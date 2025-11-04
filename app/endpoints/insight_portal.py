from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.schemas.insight_portal import InsightPortal, SocialPlatformMention
from app.schemas.utility import APIResponse
from app.core.database import get_db
from app.services.insight_portal import InsightPortalService
from app.services.ai_provider import OpenAIProvider
from app.utils.deps import get_current_user
from app.models.user import User
from app.crud.chat_message import chat_message
from app.utils.logger import setup_logger
import random

router = APIRouter()

logger = setup_logger("insight_portal", "account.log")
insight_portal_service = InsightPortalService(ai_provider=OpenAIProvider())

async def get_chat_context_for_insights(conversation_id: int, db: Session, current_user: User) -> str:
    from app.models.conversation import Conversation as ConversationModel
    conversation = db.query(ConversationModel).filter(
        ConversationModel.id == conversation_id,
        ConversationModel.user_id == current_user.id
    ).first()

    if not conversation:
        raise ValueError("Conversation not found or access denied")

    messages = chat_message.get_by_conversation_id(db, conversation_id=conversation_id)
    recent_messages = messages[-20:]

    if not recent_messages:
        return "No conversation history available."

    user_messages = [msg.content for msg in recent_messages if msg.role == "user"]

    if not user_messages:
        return "No user messages in conversation."

    key_topics = extract_key_topics_from_chat(user_messages)

    context_parts = []

    if key_topics:
        context_parts.append(f"User has been discussing these ingredients/topics: {', '.join(key_topics)}")

    recent_user_msgs = user_messages[-5:]
    if recent_user_msgs:
        context_parts.append(f"Recent conversation topics: {'; '.join(recent_user_msgs)}")

    return "\n".join(context_parts)

def extract_key_topics_from_chat(messages: list) -> list:
    ingredient_keywords = {
        'sugar', 'stevia', 'sucralose', 'aspartame', 'monk fruit', 'erythritol', 'xylitol',
        'milk', 'dairy', 'almond milk', 'oat milk', 'soy milk', 'coconut milk',
        'protein', 'whey', 'casein', 'pea protein', 'hemp protein', 'collagen',
        'berries', 'strawberry', 'blueberry', 'raspberry', 'apple', 'banana', 'orange',
        'spinach', 'kale', 'broccoli', 'carrot', 'beet', 'ginger', 'turmeric',
        'caffeine', 'vitamin', 'mineral', 'antioxidant', 'fiber', 'probiotic',
        'organic', 'natural', 'vegan', 'gluten-free', 'keto', 'low-carb'
    }

    found_topics = set()

    for message in messages:
        message_lower = message.lower()
        for keyword in ingredient_keywords:
            if keyword in message_lower:
                found_topics.add(keyword)

    return list(found_topics)

@router.get("/", response_model=APIResponse)
async def get_insight_portal(
    conversation_id: Optional[int] = Query(None, description="Conversation ID to use as context for personalized insights"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    chat_context = None
    if conversation_id:
        try:
            chat_context = await get_chat_context_for_insights(conversation_id, db, current_user)
            logger.info(f"Using chat context from conversation {conversation_id} for insights")
        except Exception as e:
            logger.warning(f"Failed to extract chat context: {str(e)}. Using generic insights.")
            chat_context = None

    social_platforms = ["tiktok", "reddit", "instagram", "facebook", "x", "pinterest"]
    top_ingredient_mentions = {}
    for platform in social_platforms:
        count = random.randint(1000, 10000)
        trend_direction = random.choice(["up", "down", "stable"])
        change_percentage = round(random.uniform(0.1, 5.0), 1)
        change_sign = "+" if trend_direction == "up" else "-" if trend_direction == "down" else ""
        change_str = f"{change_sign}{change_percentage}%"

        top_ingredient_mentions[platform] = SocialPlatformMention(
            count=count,
            trend=trend_direction,
            change=change_str
        )

    ai_generated_data = await insight_portal_service.generate_portal_insights_with_context(
        ingredient_name="General Ingredient",
        chat_context=chat_context
    )

    assistant_recommendations_dict = ai_generated_data.assistant_recommendations.model_dump()
    gender_bias_dict = ai_generated_data.gender_bias.model_dump()
    shared_product_concepts_list = [item.model_dump() for item in ai_generated_data.shared_product_concepts]

    return APIResponse(
        message="Insight portal data retrieved successfully",
        data=InsightPortal(
            top_ingredient_mentions=top_ingredient_mentions,
            shared_product_concepts=shared_product_concepts_list,
            company_competitors=ai_generated_data.company_competitors,
            assistant_recommendations=assistant_recommendations_dict,
            demography_data=ai_generated_data.demography_data,
            gender_bias=gender_bias_dict,
            top_geographic_locations=ai_generated_data.top_geographic_locations,
        )
    )
