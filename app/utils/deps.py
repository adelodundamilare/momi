from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.crud.user import user as user_crud
from app.models.user import User
from app.crud.token_denylist import token_denylist as token_denylist_crud

http_bearer = HTTPBearer()

async def get_current_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer)
) -> User:
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=["HS256"]
        )

        # Check if token is in denylist
        jti = payload.get("jti")
        if jti and token_denylist_crud.get_by_jti(db, jti=jti):
            raise HTTPException(status_code=401, detail="Token has been revoked")

        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = user_crud.get_by_email(db, email=email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

async def get_current_user_optional(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer)
) -> User:
    """Get current user if authenticated, otherwise return None."""
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=["HS256"]
        )

        # Check if token is in denylist
        jti = payload.get("jti")
        if jti and token_denylist_crud.get_by_jti(db, jti=jti):
            return None  # Token revoked, treat as unauthenticated

        email: str = payload.get("sub")
        if email is None:
            return None  # Invalid token, treat as unauthenticated
    except JWTError:
        return None  # Invalid token, treat as unauthenticated

    user = user_crud.get_by_email(db, email=email)
    return user  # Return user if found, None if not
