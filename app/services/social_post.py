from sqlalchemy.orm import Session
from faker import Faker
import random
from datetime import datetime, timedelta

from app.crud.social_post import social_post as social_post_crud
from app.schemas.social_post import SocialPostCreate

class SocialPostService:
    def __init__(self):
        self.fake = Faker()
        self.platforms = ["TikTok", "Reddit", "Instagram"]
        self.topics = [
            "Moringa benefits", "Spirulina recipes", "Turmeric lattes", 
            "Ashwagandha for stress", "Collagen for skin", "Plant-based protein",
            "Sustainable packaging", "Upcycled ingredients", "Gut health trends"
        ]

    def generate_social_posts(self, db: Session, count: int) -> list:
        """Generates and saves a specified number of mock social posts."""
        created_posts = []
        for _ in range(count):
            platform = random.choice(self.platforms)
            author = self.fake.user_name()
            content = self.fake.paragraph(nb_sentences=random.randint(2, 5)) + " #" + random.choice(self.topics).replace(" ", "")
            post_date = self.fake.date_time_between(start_date="-30d", end_date="now", tzinfo=None)
            likes = self.fake.random_int(min=0, max=1000)
            comments = self.fake.random_int(min=0, max=100)

            post_in = SocialPostCreate(
                platform=platform,
                author=author,
                content=content,
                post_date=post_date,
                likes=likes,
                comments=comments
            )
            
            created_post = social_post_crud.create(db, obj_in=post_in)
            created_posts.append(created_post)
        
        return created_posts

    def get_social_posts(self, db: Session, skip: int, limit: int):
        return db.query(social_post_crud.model).offset(skip).limit(limit).all()
