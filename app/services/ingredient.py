from sqlalchemy.orm import Session
from app.crud.ingredient import ingredient as ingredient_crud
from app.schemas.ingredient import IngredientCreate, IngredientUpdate
from fastapi import HTTPException, status
from app.services.ai_provider import AIProvider, AIProviderError
from faker import Faker
import random
import logging
from app.crud.supplier import supplier as supplier_crud
from app.schemas.supplier import SupplierCreate

logger = logging.getLogger(__name__)

class IngredientService:
    def __init__(self, ai_provider: AIProvider):
        self.ai_provider = ai_provider
        self.fake = Faker()

    def create_ingredient(self, db: Session, *, ingredient_data: IngredientCreate):
        existing_ingredient = ingredient_crud.get_by_slug(db, slug=ingredient_data.slug)
        if existing_ingredient:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"An ingredient with the slug '{ingredient_data.slug}' already exists."
            )
        new_ingredient = ingredient_crud.create(db, obj_in=ingredient_data)

        # Generate and attach mock suppliers
        num_suppliers = random.randint(0, 10)
        for _ in range(num_suppliers):
            mock_supplier_data = SupplierCreate(
                full_name=self.fake.company(),
                avatar=self.fake.image_url(),
                image=self.fake.image_url(),
                title=self.fake.job(),
                availability=random.choice(["In Stock", "Limited", "Pre-order"]),
                description=self.fake.paragraph(nb_sentences=2),
                price_per_unit=round(random.uniform(5.0, 50.0), 2),
                moq_weight_kg=random.choice([10, 25, 50, 100]),
                delivery_duration=random.choice(["1-3 days", "1 week", "2 weeks"]),
                us_approved_status=self.fake.boolean()
            )
            created_supplier = supplier_crud.create(db, obj_in=mock_supplier_data)
            new_ingredient.suppliers.append(created_supplier)

        db.commit()
        db.refresh(new_ingredient)
        return new_ingredient

    def get_ingredient(self, db: Session, id: int):
        return ingredient_crud.get(db, id=id)

    def get_by_slug(self, db: Session, slug: str):
        return ingredient_crud.get_by_slug(db, slug=slug)

    def get_ingredients(self, db: Session, skip: int = 0, limit: int = 100, search: str | None = None):
        return ingredient_crud.get_multi(db, skip=skip, limit=limit, search=search)

    async def enrich_ingredient_with_ai(self, db: Session, ingredient_id: int):
        ingredient = self.get_ingredient(db, ingredient_id)
        if not ingredient:
            # This should not happen if called from a valid context, but good to have.
            logger.warning(f"Attempted to enrich non-existent ingredient with ID: {ingredient_id}")
            return

        try:
            ai_generated_data = await self.ai_provider.generate_ingredient_enrichment(ingredient.name)
            if not ai_generated_data:
                logger.warning(f"AI provider returned no data for ingredient enrichment: {ingredient.name}")
                return ingredient

            ingredient_update_data = IngredientUpdate(
                description=ai_generated_data.description,
                benefits=ai_generated_data.benefits,
                claims=ai_generated_data.claims,
                regulatory_notes=ai_generated_data.regulatory_notes,
                function=ai_generated_data.function,
                weight=ai_generated_data.weight,
                unit=ai_generated_data.unit,
                allergies=ai_generated_data.allergies,
            )
            return ingredient_crud.update(db, db_obj=ingredient, obj_in=ingredient_update_data)
        except AIProviderError as e:
            # Log the error but don't let it crash the parent process (e.g., formula generation)
            logger.error(f"AI enrichment failed for ingredient '{ingredient.name}' (ID: {ingredient_id}): {e}")
            return ingredient # Return the original ingredient
