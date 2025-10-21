
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from datetime import datetime
from jose import jwt

from app.core.database import get_db
from app.core.config import settings
from app.core.security import create_access_token
from app.crud.user import user as user_crud
from app.crud.token_denylist import token_denylist as token_denylist_crud
from app.schemas import auth as auth_schema
from app.schemas.token_denylist import TokenDenylistCreate
from app.services.email import EmailService
from app.utils.logger import setup_logger
from app.services.user import UserService
from app.services.auth import AuthService
from app.services.oauth import oauth_service
from app.schemas.utility import APIResponse

logger = setup_logger("auth_api", "auth.log")

router = APIRouter()
http_bearer = HTTPBearer()

user_service = UserService()
auth_service = AuthService()

@router.post("/signup", response_model=APIResponse)
async def signup(user_data: auth_schema.UserCreate, db: Session = Depends(get_db)):
    try:

        user = user_service.create_user(db, user_data=user_data)

        return APIResponse(message="User created successfully", data={"user_id": user.id, "email": user.email})
    except Exception as e:
        logger.error(f"Signup failed: {str(e)}")
        raise

@router.post("/login/email", response_model=APIResponse)
async def email_login(user_data: auth_schema.UserLogin, db: Session = Depends(get_db)):
    try:
        user = user_service.find_user_by_email(db, email=user_data.email)

        if not auth_service.verify_password(user_data.password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")

        # Check for weak passwords on login and force reset
        password = user_data.password
        if len(password) < 8 or password.isdigit() or password.isalpha():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Your password is weak and no longer meets our security requirements. Please reset your password using the 'Forgot Password' link."
            )

        access_token = create_access_token(data={"sub": user.email})
        return APIResponse(message="Login successful", data={"access_token": access_token, "token_type": "bearer"})
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise



@router.post("/login/google", response_model=APIResponse)
async def google_login(
    token: str,
    db: Session = Depends(get_db)
):
    try:
        user_data = await oauth_service.verify_google_token(token)
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Google token"
            )

        user = user_crud.get_by_email(db, email=user_data["email"])
        if not user:
            user = user_crud.create(
                db,
                obj_in=auth_schema.UserCreate(
                    password="".join(oauth_service.generate_random_password()),
                    email=user_data["email"],
                    full_name=user_data["name"],
                    auth_provider="google"
                )
            )

        access_token = create_access_token(data={"sub": user.email})
        logger.info(f"Google login successful: {user.email}")
        return APIResponse(message="Google login successful", data={"access_token": access_token, "token_type": "bearer"})
    except Exception as e:
        logger.error(f"Google login failed: {str(e)}")
        raise

@router.post("/login/apple", response_model=APIResponse)
async def apple_login(
    token: str,
    db: Session = Depends(get_db)
):
    try:
        user_data = await oauth_service.verify_apple_token(token)
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Apple token"
            )

        # Similar implementation as Google login
        return APIResponse(message="Apple login successful", data={"access_token": "mock_token", "token_type": "bearer"}) # Mock data for now
    except Exception as e:
        logger.error(f"Apple login failed: {str(e)}")
        raise


@router.post("/request-forgot-password", response_model=APIResponse)
async def request_forgot_password(reset_data: auth_schema.UserEmail, db: Session = Depends(get_db)):
    try:
        user = user_service.find_user_by_email(db, email=reset_data.email)
        reset_token = auth_service.request_forget_password(db, user)

        if not reset_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password reset token not generated"
            )

        reset_link = f"{reset_data.frontend_url}?token={reset_token}" if reset_data.frontend_url else reset_token

        EmailService.send_email(
            to_email=user.email,
            subject="Reset Your Password",
            template_name="reset_password.html",
            template_context={
                "full_name": user.full_name,
                "reset_link": reset_link
            }
        )

        logger.info(f"Password reset link sent to: {user.email}")
        return APIResponse(message="Reset link sent to email")
    except Exception as e:
        logger.error(f"Password reset failed: {str(e)}")
        raise



@router.post("/reset-password", response_model=APIResponse)
async def reset_password(reset_data: auth_schema.PasswordResetConfirm, db: Session = Depends(get_db)):
    try:
        user = user_service.find_user_by_email(db, email=reset_data.email)
        auth_service.change_password_via_token(db, user, reset_data)

        EmailService.send_email(
            to_email=user.email,
            subject="Password Reset Successfully",
            template_name="reset-password-success.html",
            template_context={}
        )

        return APIResponse(message="Password Reset Successfully")
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise

@router.post("/logout", response_model=APIResponse)
async def logout(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer)
):
   try:
       token = credentials.credentials
       payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
       jti = payload.get("jti")
       exp = datetime.fromtimestamp(payload.get("exp"))

       obj_in = TokenDenylistCreate(jti=jti, exp=exp)
       token_denylist_crud.create(db, obj_in=obj_in)

       return APIResponse(message="Logged out successfully")
   except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise