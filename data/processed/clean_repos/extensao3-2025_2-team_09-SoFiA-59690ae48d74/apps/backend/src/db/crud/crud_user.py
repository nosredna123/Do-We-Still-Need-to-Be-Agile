import datetime
from typing import Any

from sqlalchemy.orm import Session, joinedload

from src.db.models.models import User
from ..models import models
from ..schemas import user as user_schema


def get_user(db: Session, user_id: int) -> type[User]:
    """
    Retrieve a single user by their ID.
    Eagerly loads salary recurrence info to populate the schema.
    """
    return (
        db.query(models.User)
        .options(
            joinedload(models.User.salary_recurrence)
            .joinedload(models.RecurrentTransaction.base_transaction)
        )
        .filter(models.User.id == user_id)
        .first()
    )


def get_existing_user(db: Session) -> type[User]:
    """
    Check if ANY user exists in the system.
    """
    return db.query(models.User).first()


def create_user(
        db: Session, user: user_schema.UserCreate, commit: bool = True
) -> models.User:
    """
    Create a new user.

    Args:
        db: Database session.
        user: User creation schema.
        commit: If True, commits transaction immediately.
                If False, flushes only (useful for atomic multi-step operations).
    """
    now = datetime.datetime.now()
    db_user = models.User(
        name=user.name,
        profile_pic=user.profile_pic,
        api_key=user.api_key,
        updated_at=now,
    )
    db.add(db_user)

    if commit:
        db.commit()
        db.refresh(db_user)
    else:
        db.flush()
        db.refresh(db_user)

    return db_user


def update_user(
        db: Session, user_id: int, user_update: user_schema.UserUpdate
) -> type[User] | None:
    """
    Update an existing user.
    Updates updated_at to now().
    """
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    db_user.updated_at = datetime.datetime.now()
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user