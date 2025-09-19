
from pydantic import BaseModel, EmailStr, field_validator, model_validator
from typing import Optional, Any
from enum import Enum

class SubscriptionPlan(str, Enum):
    FREE = "free"
    MONTHLY = "monthly"
    YEARLY = "yearly"

class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    subscription_plan: Optional[SubscriptionPlan] = SubscriptionPlan.FREE

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    avatar: Optional[str] = None

    @field_validator("full_name")
    def not_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Full name cannot be empty")
        return v

    @model_validator(mode='before')
    @classmethod
    def at_least_one_value(cls, data: Any):
        if isinstance(data, dict) and not any(data.values()):
            raise ValueError("At least one field must be provided for update")
        return data

class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    subscription_plan: SubscriptionPlan
    auth_provider: str

    class Config:
        from_attributes = True