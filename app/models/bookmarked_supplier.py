from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class BookmarkedSupplier(Base):
    __tablename__ = "bookmarked_suppliers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)

    user = relationship("User", back_populates="bookmarks")
    supplier = relationship("Supplier", back_populates="bookmarked_by")
