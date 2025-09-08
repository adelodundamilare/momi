from sqlalchemy import Column, Integer, String, JSON
from app.core.database import Base

class MockConsumer(Base):
    __tablename__ = "mock_consumers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    age = Column(Integer)
    location = Column(String)
    email = Column(String, index=True)
    job_title = Column(String)
    purchasing_history = Column(JSON)
