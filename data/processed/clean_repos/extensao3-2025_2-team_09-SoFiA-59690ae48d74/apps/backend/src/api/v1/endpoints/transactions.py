from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
import datetime

from ....db.crud import crud_transaction
from ....db.schemas import transaction as transaction_schema
from ....db.database.connection import get_db
from ....utils.constants import APPLICATION_USER_ID

router = APIRouter()


@router.post(
    "",
    response_model=transaction_schema.Transaction,
    status_code=status.HTTP_201_CREATED,
)
def create_new_transaction(
    transaction: transaction_schema.TransactionCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new transaction (either an expense or an income).

    - To create an **expense**, provide `transaction_type: "expense"`, a `category_id`.
    - To create an **income**, provide `transaction_type: "income"` and omit the category and superfluous fields.
    """
    return crud_transaction.create_transaction(
        db=db, transaction=transaction, user_id=APPLICATION_USER_ID
    )


@router.get("", response_model=List[transaction_schema.Transaction])
def read_transactions(
    skip: int = 0,
    limit: int = 100,
    date_from: Optional[datetime.date] = None,
    date_to: Optional[datetime.date] = None,
    category_id: Optional[int] = None,
    transaction_type: Optional[transaction_schema.TransactionType] = None,
    db: Session = Depends(get_db),
):
    """
    Retrieve transactions with powerful filtering options.
    """
    transactions = crud_transaction.get_transactions(
        db,
        skip=skip,
        limit=limit,
        date_from=date_from,
        date_to=date_to,
        category_id=category_id,
        transaction_type=transaction_type,
    )
    return transactions
