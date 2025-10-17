from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.schemas.supplier import Supplier
from app.crud.supplier import supplier
from app.schemas.utility import APIResponse
from app.utils.deps import get_current_user
from app.models.user import User
from app.services.supplier import SupplierService
from app.utils.logger import setup_logger

logger = setup_logger("supplier_api", "supplier.log")

router = APIRouter()
supplier_service = SupplierService()

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
    try:
        query = db.query(supplier.model)
        if search:
            query = query.filter(supplier.model.full_name.contains(search))
        if min_price is not None:
            query = query.filter(supplier.model.price_per_unit >= min_price)
        if max_price is not None:
            query = query.filter(supplier.model.price_per_unit <= max_price)
        if min_moq is not None:
            query = query.filter(supplier.model.moq_weight_kg >= min_moq)
        if max_moq is not None:
            query = query.filter(supplier.model.moq_weight_kg <= max_moq)
        if us_approved is not None:
            query = query.filter(supplier.model.us_approved_status == us_approved)
        suppliers = query.offset(skip).limit(limit).all()
        suppliers_response = [Supplier.from_orm(s) for s in suppliers]
        return APIResponse(message="Suppliers retrieved successfully", data=suppliers_response)
    except Exception as e:
        logger.error(f"Error in read_suppliers: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/{supplier_id}/bookmark", response_model=APIResponse)
def bookmark_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Bookmark a supplier for the current user.
    """
    try:
        action = supplier_service.bookmark_supplier(db=db, supplier_id=supplier_id, current_user=current_user)
        return APIResponse(message=f"Supplier {action} successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error in bookmark_supplier: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/bookmarked", response_model=APIResponse)
def get_bookmarked_suppliers(
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve bookmarked suppliers for the current user.
    """
    try:
        bookmarked = supplier_service.get_bookmarked_suppliers(current_user=current_user)
        bookmarked_response = [Supplier.from_orm(b) for b in bookmarked]
        return APIResponse(message="Bookmarked suppliers retrieved successfully", data=bookmarked_response)
    except Exception as e:
        logger.error(f"Error in get_bookmarked_suppliers: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/by-ingredient/{ingredient_id}", response_model=APIResponse)
def get_suppliers_by_ingredient(
    ingredient_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of suppliers for a given ingredient.
    """
    try:
        suppliers = supplier_service.get_suppliers_by_ingredient(db, ingredient_id)
        suppliers_response = [Supplier.from_orm(s) for s in suppliers]
        return APIResponse(message="Suppliers retrieved successfully", data=suppliers_response)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error in get_suppliers_by_ingredient: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
