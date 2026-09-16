import datetime

from pydantic import BaseModel, Field
from typing import Optional, Union, Literal, Annotated
from src.utils.enums import TransactionType


class TransactionCore(BaseModel):
    amount: Annotated[
        int,
        Field(gt=0, description="The transaction amount in cents (always positive)"),
    ]
    description: str
    reference_date: Optional[datetime.date] = None


class ExpenseCreate(TransactionCore):
    transaction_type: Literal[TransactionType.EXPENSE] = TransactionType.EXPENSE
    category_id: int


class IncomeCreate(TransactionCore):
    transaction_type: Literal[TransactionType.INCOME] = TransactionType.INCOME
    category_id: Literal[None] = None


TransactionCreate = Annotated[
    Union[ExpenseCreate, IncomeCreate], Field(discriminator="transaction_type")
]


class Transaction(TransactionCore):
    id: int
    transaction_type: TransactionType
    reference_date: datetime.date
    category_id: Optional[int] = None
    user_id: int
    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]

    class Config:
        from_attributes = True
