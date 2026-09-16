from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session

from src.db.database.connection import get_db
from src.db.schemas import recurrent as recurrent_schema
from src.services.recurrence_service import RecurrenceService
from src.utils.constants import APPLICATION_USER_ID

router = APIRouter()

def get_recurrence_service(db: Session = Depends(get_db)) -> RecurrenceService:
    return RecurrenceService(db)

@router.get(
    "",
    response_model=List[recurrent_schema.RecurrentTransactionRead],
    status_code=status.HTTP_200_OK,
    summary="List all recurrences"
)
def read_recurrences(
        skip: int = 0,
        limit: int = 100,
        service: RecurrenceService = Depends(get_recurrence_service)
):
    """
    Get all recurrence rules for the user.
    Includes both active and inactive rules.
    """
    return service.get_all_by_user(user_id=APPLICATION_USER_ID, skip=skip, limit=limit)

@router.post(
    "",
    response_model=recurrent_schema.RecurrentTransactionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new recurrence"
)
def create_recurrence(
        recurrence_data: recurrent_schema.RecurrenceInput,
        service: RecurrenceService = Depends(get_recurrence_service)
):
    """
    Creates a new Recurrent Transaction.

    This creates two entities:
    1. A **Base Transaction** (Hidden, acts as a template).
    2. A **Recurrence Rule** that points to the base transaction.
    """
    return service.create_recurrence_from_api(user_id=APPLICATION_USER_ID, input_data=recurrence_data)

@router.patch(
    "/{recurrence_id}",
    response_model=recurrent_schema.RecurrentTransactionRead,
    status_code=status.HTTP_200_OK,
    summary="Update a recurrence"
)
def update_recurrence(
        update_data: recurrent_schema.RecurrenceUpdate,
        recurrence_id: int = Path(..., description="ID of the recurrence to update"),
        service: RecurrenceService = Depends(get_recurrence_service)
):
    """
    Updates a recurrence rule.

    Can update:
    - Rule settings (Day, Frequency, Active Status)
    - Base Transaction details (Amount, Description, Category)
    """
    updated_obj = service.update_recurrence(
        user_id=APPLICATION_USER_ID,
        recurrence_id=recurrence_id,
        update_data=update_data
    )

    if not updated_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recurrence not found."
        )

    return updated_obj