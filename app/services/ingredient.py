from sqlalchemy.orm import Session
from app.crud.ingredient import ingredient as ingredient_crud
from app.schemas.ingredient import IngredientCreate, IngredientUpdate
from fastapi import HTTPException, status
from app.services.ai_provider import AIProvider, OpenAIProvider
from faker import Faker
import random
from app.crud.supplier import supplier as supplier_crud
from app.schemas.supplier import SupplierCreate

class IngredientService:
    def __init__(self):
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
            new_ingredient.suppliers.append(created_supplier) # Establish relationship

        db.commit()
        db.refresh(new_ingredient)
        return new_ingredient

    def get_ingredient(self, db: Session, id: int):
        return ingredient_crud.get(db, id=id)

    def get_by_slug(self, db: Session, slug: str):
        return ingredient_crud.get_by_slug(db, slug=slug)

    def get_ingredients(self, db: Session, skip: int = 0, limit: int = 100, search: str | None = None):
        return ingredient_crud.get_multi(db, skip=skip, limit=limit, search=search)

    def enrich_ingredient_with_ai(self, db: Session, ingredient_id: int, ai_provider: AIProvider = OpenAIProvider()):
        ingredient = self.get_ingredient(db, ingredient_id)
        if not ingredient:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingredient not found")

        # Generate AI-powered description, benefits, claims, regulatory notes, function
        ai_generated_data = ai_provider.generate_ingredient_enrichment(ingredient.name)

        # Update the ingredient with AI-generated data
        ingredient_update_data = IngredientUpdate(
            description=ai_generated_data.get("description"),
            benefits=ai_generated_data.get("benefits"),
            claims=ai_generated_data.get("claims"),
            regulatory_notes=ai_generated_data.get("regulatory_notes"),
            function=ai_generated_data.get("function"),
            weight=ai_generated_data.get("weight"),
            unit=ai_generated_data.get("unit"),
            allergies=ai_generated_data.get("allergies"),
        )
        return ingredient_crud.update(db, db_obj=ingredient, obj_in=ingredient_update_data)


