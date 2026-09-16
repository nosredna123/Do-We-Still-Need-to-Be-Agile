from typing import Optional, Any
from pydantic import BaseModel, Field, model_validator
import datetime

class UserBase(BaseModel):
    name: str
    profile_pic: Optional[str] = None
    api_key: Optional[str] = None


class UserCreate(UserBase):
    salary: Optional[int] = Field(None, description="Monthly salary in cents")
    payday: Optional[int] = Field(None, ge=1, le=31, description="Day of the month for salary receipt")


class UserUpdate(BaseModel):
    name: Optional[str] = None
    profile_pic: Optional[str] = None
    api_key: Optional[str] = None


class UserSalary(BaseModel):
    amount: int
    payday: int


class User(UserBase):
    id: int
    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]
    salary_recurrence_id: Optional[int] = None
    salary: Optional[UserSalary] = None

    @model_validator(mode='before')
    @classmethod
    def populate_salary_details(cls, data: Any) -> Any:
        """
        Inspects the ORM object (data). If a salary_recurrence exists,
        extracts the amount from the base_transaction and the day from the recurrence rule.
        """
        if hasattr(data, "salary_recurrence") and data.salary_recurrence:
            recurrence = data.salary_recurrence
            if recurrence.base_transaction:
                salary_data = {
                    "amount": recurrence.base_transaction.amount,
                    "payday": recurrence.recurrence_day
                }
                data.salary = salary_data

        return data

    class Config:
        from_attributes = True