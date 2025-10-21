from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str

    @field_validator("password")
    def validate_password(cls, v):
        if not v or not v.strip():
            raise ValueError("Password cannot be empty or contain only whitespace.")
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if v.isdigit():
            raise ValueError("Password cannot be all numbers.")
        if v.isalpha():
            raise ValueError("Password cannot be all letters.")
        return v

class Token(BaseModel):
    access_token: str
    token_type: str

class PasswordResetConfirm(BaseModel):
    email: EmailStr
    token: str
    new_password: str

class UserEmail(BaseModel):
    email: EmailStr
    frontend_url: Optional[str] = None