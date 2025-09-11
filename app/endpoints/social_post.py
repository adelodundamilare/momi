from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.social_post import SocialPost
from app.services.social_post import SocialPostService
from app.schemas.utility import APIResponse

router = APIRouter()

service = SocialPostService()

@router.post("/generate", response_model=APIResponse, status_code=201)
def generate_social_posts(
    *, 
    db: Session = Depends(get_db),
    count: int = Query(10, ge=1, le=100, description="Number of social posts to generate (1-100)")
):
    """
    Generate a specified number of mock social posts and save them to the database.
    """
    generated = service.generate_social_posts(db, count=count)
    return APIResponse(message=f"Successfully generated {len(generated)} social posts.")

@router.get("/", response_model=APIResponse)
def read_social_posts(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    Retrieve a list of mock social posts with pagination.
    """
    posts = service.get_social_posts(db, skip=skip, limit=limit)
    posts_response = [SocialPost.from_orm(post) for post in posts]
    return APIResponse(message="Social posts retrieved successfully", data=posts_response)
