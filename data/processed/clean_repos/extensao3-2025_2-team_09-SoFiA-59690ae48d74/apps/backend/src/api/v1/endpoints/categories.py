from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ....db.crud import crud_category
from ....db.schemas import category as category_schema
from ....db.database.connection import get_db

router = APIRouter()


@router.post(
    "", response_model=category_schema.Category, status_code=status.HTTP_201_CREATED
)
def create_new_category(
    category: category_schema.CategoryCreate, db: Session = Depends(get_db)
):
    """
    Create a new category.
    """
    db_category = crud_category.get_category_by_name(db, name=category.name)
    if db_category:
        raise HTTPException(
            status_code=400, detail=f"Category '{category.name}' already exists."
        )
    return crud_category.create_category(db=db, category=category)


@router.get("", response_model=List[category_schema.Category])
def read_categories(
    skip: int = 0,
    limit: int = 100,
    name_contains: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    Retrieve all categories.
    """
    categories = crud_category.get_categories(
        db, skip=skip, limit=limit, name_contains=name_contains
    )
    return categories
