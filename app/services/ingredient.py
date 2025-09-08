from sqlalchemy.orm import Session
from app.crud.ingredient import ingredient as ingredient_crud
from app.schemas.ingredient import IngredientCreate
from fastapi import HTTPException, status

class IngredientService:
    def create_ingredient(self, db: Session, *, ingredient_data: IngredientCreate):
        existing_ingredient = ingredient_crud.get_by_name(db, name=ingredient_data.name)
        if existing_ingredient:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"An ingredient with the name '{ingredient_data.name}' already exists."
            )
        return ingredient_crud.create(db, obj_in=ingredient_data)

    def get_ingredient(self, db: Session, id: int):
        return ingredient_crud.get(db, id=id)

    def get_ingredients(self, db: Session, skip: int = 0, limit: int = 100, search: str | None = None):
        return ingredient_crud.get_multi(db, skip=skip, limit=limit, search=search)

    def seed_ingredients(self, db: Session):
        sample_ingredients = [
            {
                "name": "Moringa Powder",
                "description": "Nutrient-rich superfood powder from the Moringa oleifera tree.",
                "cost": 15.50,
                "vendor": "SuperFoods Inc.",
                "benefits": "High in antioxidants, vitamins, and minerals; supports energy and immunity.",
                "claims": "Organic, Non-GMO, Vegan, Gluten-Free",
                "regulatory_notes": "Generally Recognized As Safe (GRAS) by FDA."
            },
            {
                "name": "Spirulina Algae",
                "description": "Blue-green algae known for its high protein and vitamin content.",
                "cost": 12.00,
                "vendor": "Ocean Harvest",
                "benefits": "Excellent source of protein, B vitamins, and iron; detoxifying properties.",
                "claims": "Organic, Non-GMO, Vegan",
                "regulatory_notes": "Widely used as a dietary supplement."
            },
            {
                "name": "Turmeric Extract",
                "description": "Concentrated extract from the turmeric root, standardized for curcuminoids.",
                "cost": 20.00,
                "vendor": "Spice Innovations",
                "benefits": "Potent anti-inflammatory and antioxidant effects; supports joint health.",
                "claims": "Standardized to 95% Curcuminoids",
                "regulatory_notes": "Commonly used in food and supplements."
            },
            {
                "name": "Ashwagandha Root",
                "description": "Adaptogenic herb used in Ayurvedic medicine to reduce stress.",
                "cost": 18.75,
                "vendor": "Ancient Botanicals",
                "benefits": "Helps manage stress, improves sleep quality, supports cognitive function.",
                "claims": "Organic, Adaptogenic",
                "regulatory_notes": "Popular in traditional medicine; growing scientific interest."
            },
            {
                "name": "Collagen Peptides",
                "description": "Hydrolyzed collagen for easy absorption, sourced from grass-fed bovine.",
                "cost": 25.00,
                "vendor": "Vital Proteins",
                "benefits": "Supports skin elasticity, joint health, and strong hair and nails.",
                "claims": "Grass-Fed, Pasture-Raised, Gluten-Free",
                "regulatory_notes": "Commonly used in dietary supplements."
            }
        ]

        created_count = 0
        for ingredient_data in sample_ingredients:
            existing_ingredient = ingredient_crud.get_by_name(db, name=ingredient_data["name"])
            if not existing_ingredient:
                ingredient_crud.create(db, obj_in=IngredientCreate(**ingredient_data))
                created_count += 1
        return created_count
