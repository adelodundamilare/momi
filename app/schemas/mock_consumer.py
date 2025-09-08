from pydantic import BaseModel, EmailStr
from typing import List, Any, Optional

# Shared properties
class MockConsumerBase(BaseModel):
    name: str
    age: int
    location: str
    email: EmailStr
    job_title: str
    purchasing_history: Optional[List[Any]] = None

# Properties to receive on item creation
class MockConsumerCreate(MockConsumerBase):
    pass

# Properties shared by models stored in DB
class MockConsumerInDBBase(MockConsumerBase):
    id: int

    class Config:
        orm_mode = True

# Properties to return to client
class MockConsumer(MockConsumerInDBBase):
    pass
