from sqlalchemy.orm import Session
from faker import Faker
import random

from app.crud.mock_consumer import mock_consumer as mock_consumer_crud
from app.schemas.mock_consumer import MockConsumerCreate

class MockConsumerService:
    def __init__(self):
        self.fake = Faker()
        self.fake_products = [
            "Organic Face Serum", "Matte Lipstick", "Hydrating Face Mask", 
            "Vitamin C Booster", "Anti-Aging Night Cream", "SPF 50 Sunscreen",
            "Exfoliating Scrub", "Collagen Peptide Powder", "Caffeine Eye Cream"
        ]

    def generate_consumers(self, db: Session, count: int) -> list:
        """Generates and saves a specified number of mock consumers."""
        created_consumers = []
        for _ in range(count):
            # Generate fake data
            name = self.fake.name()
            age = self.fake.random_int(min=18, max=75)
            location = self.fake.city()
            email = self.fake.email()
            job_title = self.fake.job()
            
            # Generate a fake purchasing history
            history_size = random.randint(1, 4)
            purchasing_history = random.sample(self.fake_products, history_size)

            consumer_in = MockConsumerCreate(
                name=name,
                age=age,
                location=location,
                email=email,
                job_title=job_title,
                purchasing_history=purchasing_history
            )
            
            created_consumer = mock_consumer_crud.create(db, obj_in=consumer_in)
            created_consumers.append(created_consumer)
        
        return created_consumers

    def get_consumers(self, db: Session, skip: int, limit: int):
        return db.query(mock_consumer_crud.model).offset(skip).limit(limit).all()
