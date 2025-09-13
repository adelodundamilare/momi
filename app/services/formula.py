from sqlalchemy.orm import Session
from app.crud.formula import formula as formula_crud
from app.crud.ingredient import ingredient as ingredient_crud
from app.schemas.formula import FormulaCreate, FormulaIngredientCreate
from app.schemas.ingredient import IngredientCreate
from app.models.user import User
from fastapi import HTTPException, status, BackgroundTasks
import json
from typing import List, Dict, Any

from app.services.ai_provider import AIProvider, OpenAIProvider # Import the new provider
from app.services.ingredient import IngredientService
from app.utils.text_utils import generate_slug
from app.crud.supplier import supplier as supplier_crud
from app.schemas.supplier import SupplierCreate
from faker import Faker
import random

class FormulaService:
    def __init__(self, ai_provider: AIProvider = OpenAIProvider()): # Inject the provider
        self.ai_provider = ai_provider
        self.ingredient_service = IngredientService()
        self.fake = Faker()

    def create_formula(self, db: Session, *, formula_data: FormulaCreate, current_user: User):
        # Validate that all ingredients exist before creating the formula
        for item in formula_data.ingredients:
            ingredient = ingredient_crud.get(db, id=item.ingredient_id)
            if not ingredient:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Ingredient with id {item.ingredient_id} not found."
                )

        return formula_crud.create_with_author(db, obj_in=formula_data, author_id=current_user.id)

    def generate_formula_from_concept(self, db: Session, product_concept: str, current_user: Any, background_tasks: BackgroundTasks) -> Any:
        # 1. Call AI to get ingredients, quantities, and estimated costs
        ai_generated_formula_details = self.ai_provider.generate_formula_details(product_concept)

        formula_name = ai_generated_formula_details.get("formula_name", product_concept)
        formula_description = ai_generated_formula_details.get("formula_description", f"Formula for {product_concept}")
        ai_ingredients = ai_generated_formula_details.get("ingredients", [])

        formula_ingredients_create = []
        for ai_ingredient in ai_ingredients:
            ingredient_name = ai_ingredient.get("name")
            quantity = ai_ingredient.get("quantity")
            suggested_supplier_name = ai_ingredient.get("suggested_supplier_name")

            if not ingredient_name or quantity is None:
                continue

            ingredient_slug = generate_slug(ingredient_name)
            existing_ingredient = ingredient_crud.get_by_slug(db, slug=ingredient_slug)

            if not existing_ingredient:
                # Create new ingredient (this will trigger supplier generation)
                new_ingredient_data = IngredientCreate(name=ingredient_name, slug=ingredient_slug)
                created_ingredient = self.ingredient_service.create_ingredient(db, ingredient_data=new_ingredient_data)
                ingredient_id = created_ingredient.id
                # AI Enrichment for new ingredient
                background_tasks.add_task(self.ingredient_service.enrich_ingredient_with_ai, db, ingredient_id=created_ingredient.id)
            else:
                ingredient_id = existing_ingredient.id

            # Find or create supplier with cheapest price
            supplier_id = None
            cheapest_supplier = supplier_crud.get_cheapest_supplier_for_ingredient(db, ingredient_id)

            if cheapest_supplier:
                supplier_id = cheapest_supplier.id
            else:
                # If no existing suppliers for this ingredient, create a new mock supplier
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
                supplier_id = created_supplier.id

            formula_ingredients_create.append(FormulaIngredientCreate(
                ingredient_id=ingredient_id,
                quantity=quantity,
                supplier_id=supplier_id # Pass supplier_id here
            ))

        # 2. Create the Formula entry and save to DB
        formula_create_data = FormulaCreate(
            name=formula_name,
            description=formula_description,
            product_concept=product_concept,
            ingredients=formula_ingredients_create,
        )

        # Save the formula to the database
        created_formula = formula_crud.create_with_author(db, obj_in=formula_create_data, author_id=current_user.id)

        return created_formula

    def get_formula(self, db: Session, id: int):
        return formula_crud.get(db, id=id)

    def suggest_ingredient_substitutions(self, ingredient_name: str) -> List[str]:
        return self.ai_provider.generate_ingredient_substitutions(ingredient_name)

    def generate_mock_nutrition_panel(self, formula_id: int) -> Dict[str, Any]:
        """
        Generates a mock Nutrition Facts Panel for a given formula.
        (No real calculations at MVP stage - static template).
        """
        # In a real scenario, you'd fetch formula details and ingredients here
        # For MVP, we return a static template.
        return {
            "serving_size": "1 scoop (30g)",
            "servings_per_container": "30",
            "amount_per_serving": {
                "calories": "120",
                "total_fat": "2g",
                "saturated_fat": "1g",
                "trans_fat": "0g",
                "cholesterol": "5mg",
                "sodium": "100mg",
                "total_carbohydrate": "5g",
                "dietary_fiber": "1g",
                "total_sugars": "2g",
                "added_sugars": "0g",
                "protein": "20g"
            },
            "vitamins_minerals": {
                "vitamin_d": "0mcg (0% DV)",
                "calcium": "130mg (10% DV)",
                "iron": "1.8mg (10% DV)",
                "potassium": "230mg (5% DV)"
            },
            "ingredients_list": "Protein Blend (Whey Protein Concentrate, Whey Protein Isolate), Natural Flavors, Xanthan Gum, Stevia Extract."
        }
