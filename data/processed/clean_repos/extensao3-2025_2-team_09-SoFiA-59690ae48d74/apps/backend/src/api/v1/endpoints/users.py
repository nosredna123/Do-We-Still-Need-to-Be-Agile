import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.db.crud import crud_user, crud_recurrence
from src.db.schemas import user as user_schema
from src.db.schemas import transaction as transaction_schema
from src.db.schemas import recurrent as recurrent_schema
from src.db.database.connection import get_db
from src.utils.constants import APPLICATION_USER_ID
from src.utils.enums import TransactionType, RecurrenceFrequency
from src.services.transaction_service import TransactionService
from src.services.recurrence_service import RecurrenceService
from src.api.deps import get_transaction_service
from src.core.logger import logger

router = APIRouter()


@router.get(
    "/me",
    response_model=user_schema.User,
    status_code=status.HTTP_200_OK,
    summary="Get the primary user details",
)
def get_user(db: Session = Depends(get_db)):
    """
    Retrieve the details of the primary application user (ID defined in constants).
    """
    db_user = crud_user.get_user(db, user_id=APPLICATION_USER_ID)

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário do aplicativo não encontrado.",
        )

    return db_user


@router.post(
    "",
    response_model=user_schema.User,
    status_code=status.HTTP_201_CREATED,
    summary="Create the primary user",
)
def create_user(
        user: user_schema.UserCreate,
        db: Session = Depends(get_db),
        transaction_service: TransactionService = Depends(get_transaction_service)
):
    """
    Create a new user.

    **Constraints**:
    - This system allows **only one user**.

    **Automatic Salary Setup**:
    - If `salary` and `payday` are provided:
      1. Creates a salary transaction Template (Base Transaction).
      2. Creates a recurrence rule.
      3. Checks if the **current month's** salary is due and generates it if missing.
         (Does NOT backfill previous months).
    """
    existing_user = crud_user.get_existing_user(db)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user already exists. This system is limited to a single user.",
        )

    try:
        new_user = crud_user.create_user(db=db, user=user, commit=False)

        if user.salary and user.payday:
            today = datetime.date.today()
            tx_create = transaction_schema.IncomeCreate(
                amount=user.salary,
                description="Salário Mensal",
                reference_date=today,
                transaction_type=TransactionType.INCOME,
                category_id=None
            )
            base_tx = transaction_service.create_transaction(
                user_id=new_user.id,
                transaction_data=tx_create
            )
            recurrence_create = recurrent_schema.RecurrentTransactionCreate(
                base_transaction_id=base_tx.id,
                recurrence_day=user.payday,
                frequency=RecurrenceFrequency.MONTHLY
            )
            recurrence = crud_recurrence.create_recurrence(
                db, recurrence_create, user_id=new_user.id, commit=False
            )
            new_user.salary_recurrence_id = recurrence.id
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            try:
                recurrence_service = RecurrenceService(db)
                recurrence_service.process_daily_recurrences()
            except Exception as e:
                logger.error(f"Failed to auto-process recurrences during user creation: {e}")
        else:
            db.commit()
            db.refresh(new_user)

        return new_user
    except Exception as e:
        logger.error(f"Failed to create user: {e}", exc_info=True)
        db.rollback() # Release locks immediately on error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user due to database error: {str(e)}"
        )


@router.put(
    "/{user_id}",
    response_model=user_schema.User,
    status_code=status.HTTP_200_OK,
    summary="Update user details",
)
def update_user(
        user_update: user_schema.UserUpdate,
        db: Session = Depends(get_db),
):
    """
    Update the user's name, profile picture, or API key.
    Only updates the fields provided in the payload.
    """
    db_user = crud_user.update_user(db=db, user_id=APPLICATION_USER_ID, user_update=user_update)

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {APPLICATION_USER_ID} not found.",
        )

    return db_user