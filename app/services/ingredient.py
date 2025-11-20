import logging
import random
from tenacity import retry, stop_after_attempt, wait_fixed, RetryError
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.crud.ingredient import ingredient as ingredient_crud
from app.crud.supplier import supplier as supplier_crud
from app.schemas.ingredient import IngredientCreate, IngredientUpdate
from app.schemas.supplier import SupplierCreate
from app.services.ai_provider import AIProvider, AIProviderError
from app.services.supplier import SupplierService
from faker import Faker
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

class IngredientService:
    def __init__(self, ai_provider: AIProvider):
        self.ai_provider = ai_provider
        self.fake = Faker()
        self.supplier_service = SupplierService()

    def create_ingredient(self, db: Session, *, ingredient_data: IngredientCreate):
        existing_ingredient = ingredient_crud.get_by_slug(db, slug=ingredient_data.slug)
        if existing_ingredient:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"An ingredient with the slug '{ingredient_data.slug}' already exists."
            )

        if not ingredient_data.image:
            ingredient_data.image = self.fake.image_url(width=640, height=480, placeholder_url='https://picsum.photos/{width}/{height}')

        new_ingredient = ingredient_crud.create(db, obj_in=ingredient_data)

        num_suppliers = random.randint(0, 10)
        for _ in range(num_suppliers):
            mock_supplier_data = SupplierCreate(
                full_name=self.fake.company(),
                avatar=self.fake.image_url(width=640, height=480, placeholder_url='https://picsum.photos/{width}/{height}'),
                image=self.fake.image_url(width=640, height=480, placeholder_url='https://picsum.photos/{width}/{height}'),
                title=self.fake.job(),
                availability=random.choice(["In Stock", "Limited", "Pre-order"]),
                description=self.fake.paragraph(nb_sentences=2),
                price_per_unit=round(random.uniform(5.0, 50.0), 2),
                moq_weight_kg=random.choice([10, 25, 50, 100]),
                delivery_duration=random.choice(["1-3 days", "1 week", "2 weeks"]),
                us_approved_status=self.fake.boolean(),
                ingredient_id=new_ingredient.id
            )
            created_supplier = self.supplier_service.create_supplier(db, mock_supplier_data)

        db.commit()
        db.refresh(new_ingredient)
        return new_ingredient

    def get_ingredient(self, db: Session, id: int):
        return ingredient_crud.get(db, id=id)

    def get_by_slug(self, db: Session, slug: str):
        return ingredient_crud.get_by_slug(db, slug=slug)

    def get_ingredients(self, db: Session, skip: int = 0, limit: int = 100, search: str | None = None):
        return ingredient_crud.get_multi(db, skip=skip, limit=limit, search=search)

    def add_supplier_to_ingredient(self, db: Session, ingredient_id: int, supplier_id: int):
        ingredient = ingredient_crud.get(db, id=ingredient_id)
        if not ingredient:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingredient not found")
        supplier = supplier_crud.get(db, id=supplier_id)
        if not supplier:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found")

        return ingredient_crud.add_supplier(db, ingredient, supplier)

    def remove_supplier_from_ingredient(self, db: Session, ingredient_id: int, supplier_id: int):
        ingredient = ingredient_crud.get(db, id=ingredient_id)
        if not ingredient:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingredient not found")
        supplier = supplier_crud.get(db, id=supplier_id)
        if not supplier:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found")

        return ingredient_crud.remove_supplier(db, ingredient, supplier)

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    async def enrich_ingredient_with_ai(self, ingredient_id: int):
        with SessionLocal() as db:
            ingredient = self.get_ingredient(db, ingredient_id)
            if not ingredient:
                logger.warning(f"Attempted to enrich non-existent ingredient with ID: {ingredient_id}")
                return

            try:
                ai_generated_data = await self.ai_provider.generate_ingredient_enrichment(ingredient.name)
                if not ai_generated_data:
                    raise AIProviderError("AI provider returned no data.")

                update_data = {
                    "description": ai_generated_data.description,
                    "benefits": ai_generated_data.benefits,
                    "claims": ai_generated_data.claims,
                    "regulatory_notes": ai_generated_data.regulatory_notes,
                    "function": ai_generated_data.function,
                    "weight": ai_generated_data.weight,
                    "unit": ai_generated_data.unit,
                    "allergies": ai_generated_data.allergies,
                    "enrichment_status": "success",
                    "enrichment_error": None,
                }
                ingredient_crud.update(db, db_obj=ingredient, obj_in=update_data)

            except Exception as e:
                logger.error(f"AI enrichment failed for ingredient '{ingredient.name}' (ID: {ingredient_id}): {e}")
                update_data = {
                    "enrichment_status": "failed",
                    "enrichment_error": str(e),
                }
                ingredient_crud.update(db, db_obj=ingredient, obj_in=update_data)
                raise
