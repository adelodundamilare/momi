from sqlalchemy.orm import Session
from app.crud.formula import formula as formula_crud
from app.crud.ingredient import ingredient as ingredient_crud
from app.schemas.formula import FormulaCreate, FormulaIngredientCreate
from app.schemas.ingredient import IngredientCreate
from app.models.user import User
from fastapi import HTTPException, status, BackgroundTasks

from typing import List, Dict, Any
from io import BytesIO

from openpyxl import Workbook
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

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
                print(f"Creating new ingredient: {ingredient_name}")
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

    def export_formula_excel(self, db: Session, formula_id: int) -> BytesIO:
        formula = self.get_formula(db, id=formula_id)
        if not formula:
            raise HTTPException(status_code=404, detail="Formula not found")

        wb = Workbook()
        ws = wb.active
        ws.title = "Formula"

        ws.append(["Name", formula.name])
        ws.append(["Description", formula.description])
        ws.append([])
        ws.append(["Ingredients"])
        ws.append(["Name", "Quantity", "Supplier", "Price per Unit", "Cost"])

        for item in formula.ingredients:
            ingredient = item.ingredient
            supplier = item.supplier
            cost = item.quantity * supplier.price_per_unit if supplier else 0
            ws.append(
                [
                    ingredient.name,
                    item.quantity,
                    supplier.full_name if supplier else "N/A",
                    supplier.price_per_unit if supplier else "N/A",
                    cost,
                ]
            )

        ws.append([])
        ws.append(["Total Cost", formula.total_cost])

        excel_file = BytesIO()
        wb.save(excel_file)
        excel_file.seek(0)

        return excel_file

    def export_formula_pdf(self, db: Session, formula_id: int) -> BytesIO:
        formula = self.get_formula(db, id=formula_id)
        if not formula:
            raise HTTPException(status_code=404, detail="Formula not found")

        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer)
        elements = []
        styles = getSampleStyleSheet()

        elements.append(Paragraph(f"Formula: {formula.name}", styles['h1']))
        elements.append(Paragraph(f"Description: {formula.description}", styles['body']))
        elements.append(Paragraph("<br/><br/>", styles['body']))

        data = [["Ingredient", "Quantity", "Supplier", "Price per Unit", "Cost"]]
        for item in formula.ingredients:
            ingredient = item.ingredient
            supplier = item.supplier
            cost = item.quantity * supplier.price_per_unit if supplier else 0
            data.append(
                [
                    ingredient.name,
                    item.quantity,
                    supplier.full_name if supplier else "N/A",
                    supplier.price_per_unit if supplier else "N/A",
                    cost,
                ]
            )
        
        data.append(["", "", "", "Total Cost", formula.total_cost])

        table = Table(data)
        style = TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -2), colors.beige),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]
        )
        table.setStyle(style)
        elements.append(table)

        doc.build(elements)
        pdf_buffer.seek(0)
        return pdf_buffer
