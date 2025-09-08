from app.crud.base import CRUDBase
from app.models.social_post import SocialPost
from app.schemas.social_post import SocialPostCreate

class CRUDSocialPost(CRUDBase[SocialPost, SocialPostCreate, None]):
    pass

social_post = CRUDSocialPost(SocialPost)
