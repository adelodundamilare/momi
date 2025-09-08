from sqlalchemy.orm import Session
from app.crud.formula import formula as formula_crud
from app.crud.ingredient import ingredient as ingredient_crud
from app.schemas.formula import FormulaCreate
from app.models.user import User
from fastapi import HTTPException, status
import openai
import json
from typing import List, Dict, Any

class FormulaService:
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4-turbo" # Model that supports JSON mode

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

    def get_formula(self, db: Session, id: int):
        return formula_crud.get(db, id=id)

    def suggest_ingredient_substitutions(self, ingredient_name: str) -> List[str]:
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
            
            # Assuming the AI returns a JSON object with a key like 'alternatives' containing the list
            response_content = json.loads(response.choices[0].message.content)
            alternatives = response_content.get("alternatives", [])

            if not isinstance(alternatives, list):
                print(f"AI did not return a list of alternatives: {alternatives}")
                return []

            return alternatives

        except Exception as e:
            print(f"Error suggesting substitutions for {ingredient_name}: {e}")
            return []

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
