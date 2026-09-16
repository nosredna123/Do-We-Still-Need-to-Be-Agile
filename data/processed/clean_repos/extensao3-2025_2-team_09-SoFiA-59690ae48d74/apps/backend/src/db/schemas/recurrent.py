from typing import Optional
from pydantic import BaseModel, Field
from src.utils.enums import RecurrenceFrequency, TransactionType
from src.db.schemas.transaction import TransactionCore

class RecurrentTransactionBase(BaseModel):
    recurrence_day: int = Field(..., ge=1, le=31, description="Day of the month to execute")
    frequency: RecurrenceFrequency = RecurrenceFrequency.MONTHLY

class RecurrentTransactionCreate(RecurrentTransactionBase):
    base_transaction_id: int

class RecurrentTransactionRead(RecurrentTransactionBase):
    id: int
    user_id: int
    base_transaction_id: int
    is_active: bool
    base_transaction: Optional[TransactionCore] = None

    class Config:
        from_attributes = True

class RecurrenceInput(TransactionCore):
    transaction_type: TransactionType
    category_id: Optional[int] = None
    recurrence_day: int = Field(..., ge=1, le=31)
    frequency: RecurrenceFrequency = RecurrenceFrequency.MONTHLY

class RecurrenceUpdate(BaseModel):
    recurrence_day: Optional[int] = Field(None, ge=1, le=31)
    frequency: Optional[RecurrenceFrequency] = None
    is_active: Optional[bool] = None
    amount: Optional[int] = Field(None, gt=0)
    description: Optional[str] = None
    category_id: Optional[int] = None