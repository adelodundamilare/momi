from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.services.ai_provider import AIProvider, OpenAIProvider, AIProviderError
from app.crud.formula import formula as formula_crud
from app.crud.marketing import marketing_copy as marketing_copy_crud
from app.models.marketing import MarketingCopy
from app.schemas.marketing import MarketingCopyCreate

class MarketingService:
    def __init__(self, ai_provider: AIProvider = OpenAIProvider()):
        self.ai_provider = ai_provider

    async def generate_for_formula(self, db: Session, formula_id: int) -> MarketingCopy:
        formula = formula_crud.get(db, id=formula_id)
        if not formula:
            raise HTTPException(status_code=404, detail="Formula not found")

        if formula.marketing_copy:
            return formula.marketing_copy

        try:
            ai_marketing_copy = await self.ai_provider.generate_marketing_copy(
                formula_name=formula.name,
                formula_description=formula.description
            )
        except AIProviderError as e:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"AI service failed to generate marketing copy: {e}")

        image_prompt = f"A professional product mockup of '{ai_marketing_copy.product_name}', a {formula.description}. The packaging should be clean, modern, and appealing to consumers. Product shot, studio lighting."
        try:
            image_url = await self.ai_provider.generate_image(image_prompt)
        except AIProviderError as e:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"AI service failed to generate product mockup: {e}")

        marketing_copy_data = MarketingCopyCreate(
            **ai_marketing_copy.dict(),
            formula_id=formula_id,
            product_mockup_url=image_url
        )

        return marketing_copy_crud.create(db, obj_in=marketing_copy_data)

    async def regenerate_mockup(self, db: Session, formula_id: int) -> MarketingCopy:
        formula = formula_crud.get(db, id=formula_id)
        if not formula:
            raise HTTPException(status_code=404, detail="Formula not found")

        marketing_copy = formula.marketing_copy
        if not marketing_copy:
            raise HTTPException(status_code=404, detail="Marketing copy not found for this formula. Please generate it first.")

        image_prompt = f"A professional product mockup of '{marketing_copy.product_name}', a {formula.description}. The packaging should be clean, modern, and appealing to consumers. Product shot, studio lighting, alternative take."
        try:
            image_url = await self.ai_provider.generate_image(image_prompt)
        except AIProviderError as e:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"AI service failed to generate product mockup: {e}")

        update_data = {"product_mockup_url": image_url}
        return marketing_copy_crud.update(db, db_obj=marketing_copy, obj_in=update_data)
