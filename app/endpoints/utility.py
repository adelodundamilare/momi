
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.crud.user import user as user_crud
from app.schemas import user as user_schema
from app.utils.deps import get_current_user
from app.utils.logger import setup_logger
from app.models.user import User
from app.services.email import EmailService
from app.services.user import UserService
from app.services.cloudinary import CloudinaryService
from app.schemas.utility import APIResponse

logger = setup_logger("utility_api", "utility.log")

router = APIRouter()
user_service = UserService()
cloudinary_service = CloudinaryService()

@router.post("/upload-to-cloud", response_model=APIResponse)
async def upload_to_cloud(
    file: UploadFile = File(...)
    # current_user: User = Depends(get_current_user),
    # db: Session = Depends(get_db)
):
    # List of allowed image content types
    allowed_image_types = ["image/jpeg", "image/png"]
    if file.content_type not in allowed_image_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Only the following are allowed: {', '.join(allowed_image_types)}"
        )

    try:
        file_bytes = await file.read()
        res = cloudinary_service.upload_file(file_bytes)
        return APIResponse(message="File uploaded successfully", data={"url": res})
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise
