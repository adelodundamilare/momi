from sqlalchemy.orm import Session
from app.crud.ingredient import ingredient as ingredient_crud
from app.schemas.ingredient import IngredientCreate, IngredientUpdate
from fastapi import HTTPException, status
from app.services.ai_provider import AIProvider, OpenAIProvider

class IngredientService:
    def create_ingredient(self, db: Session, *, ingredient_data: IngredientCreate):
        existing_ingredient = ingredient_crud.get_by_slug(db, slug=ingredient_data.slug)
        if existing_ingredient:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"An ingredient with the slug '{ingredient_data.slug}' already exists."
            )
        return ingredient_crud.create(db, obj_in=ingredient_data)

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
            cost=ai_generated_data.get("cost"),
            allergies=ai_generated_data.get("allergies"),
        )
        return ingredient_crud.update(db, db_obj=ingredient, obj_in=ingredient_update_data)

    
