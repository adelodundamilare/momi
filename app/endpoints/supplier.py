from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.schemas.supplier import Supplier
from app.crud.supplier import supplier
from app.schemas.utility import APIResponse
from app.utils.deps import get_current_user
from app.models.user import User
from app.models.bookmarked_supplier import BookmarkedSupplier

router = APIRouter()

@router.get("/", response_model=APIResponse)
def read_suppliers(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = Query(None, description="Search suppliers by name"),
    min_price: Optional[float] = Query(None, description="Minimum price per kg"),
    max_price: Optional[float] = Query(None, description="Maximum price per kg"),
    min_moq: Optional[float] = Query(None, description="Minimum MOQ weight in kg"),
    max_moq: Optional[float] = Query(None, description="Maximum MOQ weight in kg"),
    us_approved: Optional[bool] = Query(None, description="Filter by US approved status")
):
    """
    Retrieve a list of suppliers with optional search and pagination.
    """
    query = db.query(supplier.model)
    if search:
        query = query.filter(supplier.model.full_name.contains(search))
    if min_price is not None:
        query = query.filter(supplier.model.price_per_kg >= min_price)
    if max_price is not None:
        query = query.filter(supplier.model.price_per_kg <= max_price)
    if min_moq is not None:
        query = query.filter(supplier.model.moq_weight_kg >= min_moq)
    if max_moq is not None:
        query = query.filter(supplier.model.moq_weight_kg <= max_moq)
    if us_approved is not None:
        query = query.filter(supplier.model.us_approved_status == us_approved)
    suppliers = query.offset(skip).limit(limit).all()
    suppliers_response = [Supplier.from_orm(s) for s in suppliers]
    return APIResponse(message="Suppliers retrieved successfully", data=suppliers_response)

@router.post("/{supplier_id}/bookmark", response_model=APIResponse)
def bookmark_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Bookmark a supplier for the current user.
    """
    obj_in = BookmarkedSupplierCreate(user_id=current_user.id, supplier_id=supplier_id)
    bookmarked_supplier.create(db, obj_in=obj_in)
    return APIResponse(message="Supplier bookmarked successfully")

@router.get("/bookmarked", response_model=APIResponse)
def get_bookmarked_suppliers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve bookmarked suppliers for the current user.
    """
    bookmarked = db.query(Supplier).join(BookmarkedSupplier, BookmarkedSupplier.supplier_id == Supplier.id).filter(BookmarkedSupplier.user_id == current_user.id).all()
    bookmarked_response = [Supplier.from_orm(b) for b in bookmarked]
    return APIResponse(message="Bookmarked suppliers retrieved successfully", data=bookmarked_response)
