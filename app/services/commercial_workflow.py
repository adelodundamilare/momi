from datetime import date, timedelta
from typing import List
import random

from app.schemas.commercial_workflow import (
    CommercialWorkflowRequest,
    CommercialWorkflowResponse,
    TimelineStep,
    CoManufacturer
)

class CommercialWorkflowService:
    def generate_workflow_estimate(self, request: CommercialWorkflowRequest) -> CommercialWorkflowResponse:
        # Mock Timeline Generation
        today = date.today()
        timeline = []

        # Define fixed steps and their mock durations
        steps_data = [
            {"name": "Sourcing", "duration_days": 30},
            {"name": "Prototype", "duration_days": 45},
            {"name": "Testing", "duration_days": 60},
            {"name": "Launch", "duration_days": 15}
        ]

        current_date = today
        for step in steps_data:
            start_date = current_date
            end_date = start_date + timedelta(days=step["duration_days"])
            timeline.append(TimelineStep(name=step["name"], start_date=start_date, end_date=end_date))
            current_date = end_date + timedelta(days=random.randint(5, 10)) # Add a small gap

        # Mock Co-Manufacturer Selection
        all_co_manufacturers = [
            CoManufacturer(name="Global Food Co-Packers", location="California, USA"),
            CoManufacturer(name="EuroBlend Solutions", location="Berlin, Germany"),
            CoManufacturer(name="Asia Pacific Innovations", location="Singapore"),
            CoManufacturer(name="Flavor Fusion Labs", location="Ohio, USA"),
        ]

        # Select 1 or 2 random co-manufacturers
        num_manufacturers = random.randint(1, 2)
        selected_co_manufacturers = random.sample(all_co_manufacturers, num_manufacturers)

        return CommercialWorkflowResponse(
            timeline=timeline,
            co_manufacturers=selected_co_manufacturers
        )
