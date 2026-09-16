import datetime
from typing import Optional
from sqlalchemy.orm import Session
from ..schemas import transaction as transaction_schema
from ..models import models


def get_transaction(db: Session, transaction_id: int):
    return (
        db.query(models.Transaction)
        .filter(models.Transaction.id == transaction_id)
        .first()
    )


def get_transactions(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        date_from: Optional[datetime.date] = None,
        date_to: Optional[datetime.date] = None,
        category_id: Optional[int] = None,
        transaction_type: Optional[str] = None,
):
    query = db.query(models.Transaction).order_by(
        models.Transaction.reference_date.desc()
    )
    if date_from:
        query = query.filter(models.Transaction.reference_date >= date_from)
    if date_to:
        query = query.filter(models.Transaction.reference_date <= date_to)
    if category_id is not None:
        query = query.filter(models.Transaction.category_id == category_id)
    if transaction_type:
        query = query.filter(models.Transaction.transaction_type == transaction_type)

    return query.offset(skip).limit(limit).all()


def create_transaction(
        db: Session, transaction: transaction_schema.TransactionCreate, user_id: int
) -> models.Transaction:
    db_data = transaction.model_dump(exclude_unset=True)
    db_data["user_id"] = user_id
    if not db_data.get("reference_date"):
        db_data["reference_date"] = datetime.date.today()
    db_transaction = models.Transaction(**db_data)
    db.add(db_transaction)
    db.flush()
    db.refresh(db_transaction)
    return db_transaction