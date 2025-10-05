from pydantic import BaseModel
from typing import Any, Optional, Generic, TypeVar

T = TypeVar('T')

class APIResponse(BaseModel, Generic[T]):
    message: str
    data: Optional[T] = None
