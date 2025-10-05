from fastapi import HTTPException, status
from typing import Dict
from sqlalchemy.orm import Session
from datetime import datetime
import asyncio

from app.schemas.commercial_workflow_analysis import (
    AIWorkflowIngredient,
    CommercializationAnalysisOutput,
    WorkflowRequest,
    PackagingSpec,
    Task
)
from app.services.ai_provider import OpenAIProvider, AIProviderError
from app.crud.formula import formula as formula_crud

class CommercialWorkflowService:
    def __init__(self, ai_provider: OpenAIProvider = OpenAIProvider()):
        self.ai_provider = ai_provider

    async def analyze_formula(self, db: Session, formula_id: int) -> CommercializationAnalysisOutput:
        formula = formula_crud.get_with_full_details(db, id=formula_id)

        if not formula:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Formula not found")

        ingredients_for_ai = []
        for fi in formula.ingredients:
            supplier_name = fi.supplier.full_name if fi.supplier else None
            lead_time = self._parse_delivery_duration(fi.supplier.delivery_duration) if fi.supplier and fi.supplier.delivery_duration else None
            cost_per_unit = fi.supplier.price_per_unit if fi.supplier else None
            ingredients_for_ai.append(AIWorkflowIngredient(
                name=fi.ingredient.name,
                quantity=fi.quantity,
                unit=fi.ingredient.unit or "unit",
                supplier=supplier_name,
                lead_time_days=lead_time,
                cost_per_unit=cost_per_unit
            ))

        packaging_spec = PackagingSpec(
            type="Bottle",
            size="500ml",
            material="Glass",
            supplier="Generic Packaging Co."
        )

        workflow_request = WorkflowRequest(
            product_id=str(formula.id),
            product_name=formula.name,
            ingredients=ingredients_for_ai,
            packaging=packaging_spec,
            target_volume=10000,
            batch_size=1000,
            target_launch_date=None,
            budget_limit=None,
            market="US"
        )

        try:
            ai_insights_task = self.ai_provider.generate_commercialization_insights(
                formula_name=workflow_request.product_name,
                formula_description=formula.description,
                master_tasks_data=[t.model_dump() for t in self._define_base_tasks().values()]
            )

            supplier_analysis_task = self.ai_provider.generate_supplier_analysis(workflow_request.model_dump())
            cost_analysis_task = self.ai_provider.generate_cost_analysis(workflow_request.model_dump())

            ai_insights, supplier_analysis, cost_analysis = await asyncio.gather(
                ai_insights_task,
                supplier_analysis_task,
                cost_analysis_task
            )
        except AIProviderError as e:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"AI service failed: {e}")

        return CommercializationAnalysisOutput(
            product_id=workflow_request.product_id,
            product_name=workflow_request.product_name,
            generated_at=datetime.utcnow().isoformat(),
            timeline_data=ai_insights.timeline_data.model_dump(),
            risks=ai_insights.risks,
            recommendations=ai_insights.recommendations,
            supplier_analysis=supplier_analysis.model_dump(),
            cost_analysis=cost_analysis.model_dump()
        )

    def _define_base_tasks(self) -> Dict[str, Task]:
        return {
            "ingredient_procurement": Task(stage_name="Ingredient Procurement", duration_weeks=0, can_parallelize=False, dependencies=[], tasks=[], notes=""),
            "production_setup": Task(stage_name="Production Setup", duration_weeks=0, can_parallelize=False, dependencies=["ingredient_procurement"], tasks=[], notes=""),
            "manufacturing": Task(stage_name="Manufacturing", duration_weeks=0, can_parallelize=False, dependencies=["production_setup"], tasks=[], notes=""),
            "packaging": Task(stage_name="Packaging", duration_weeks=0, can_parallelize=True, dependencies=["manufacturing"], tasks=[], notes=""),
            "quality_assurance": Task(stage_name="Quality Assurance", duration_weeks=0, can_parallelize=False, dependencies=["manufacturing"], tasks=[], notes=""),
            "distribution_setup": Task(stage_name="Distribution Setup", duration_weeks=0, can_parallelize=True, dependencies=["packaging"], tasks=[], notes=""),
            "launch_preparation": Task(stage_name="Launch Preparation", duration_weeks=0, can_parallelize=False, dependencies=["quality_assurance", "distribution_setup"], tasks=[], notes=""),
        }

    def _parse_delivery_duration(self, duration_str: str) -> int:
        duration_str = duration_str.lower()
        if "day" in duration_str:
            if "-" in duration_str:
                parts = duration_str.split("-")
                return (int(parts[0].strip()) + int(parts[1].split(" ")[0].strip())) // 2
            else:
                return int(duration_str.split(" ")[0].strip())
        elif "week" in duration_str:
            if "-" in duration_str:
                parts = duration_str.split("-")
                return ((int(parts[0].strip()) + int(parts[1].split(" ")[0].strip())) // 2) * 7
            else:
                return int(duration_str.split(" ")[0].strip()) * 7
        return 0
