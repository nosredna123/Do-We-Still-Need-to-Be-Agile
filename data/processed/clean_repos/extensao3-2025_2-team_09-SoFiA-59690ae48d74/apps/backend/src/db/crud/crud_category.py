from sqlalchemy.orm import Session
from ..schemas import category as category_schema
from ..models import models
from typing import Optional


def get_categories(
    db: Session, skip: int = 0, limit: int = 100, name_contains: Optional[str] = None
):
    """
    Retrieve all categories, with an option to search by name.
    """
    query = db.query(models.Category)
    if name_contains:
        query = query.filter(models.Category.name.ilike(f"%{name_contains}%"))

    return query.offset(skip).limit(limit).all()


def get_category_by_name(db: Session, name: str):
    """
    Retrieve a single category by its name.
    """
    return db.query(models.Category).filter(models.Category.name == name).first()


def create_category(
    db: Session, category: category_schema.CategoryCreate
) -> models.Category:
    """
    Create a new category in the database.
    """
    db_category = models.Category(name=category.name)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category
