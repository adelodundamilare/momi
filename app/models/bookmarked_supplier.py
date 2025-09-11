from sqlalchemy import Column, Integer, ForeignKey
from app.core.database import Base

class BookmarkedSupplier(Base):
    __tablename__ = "bookmarked_suppliers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
