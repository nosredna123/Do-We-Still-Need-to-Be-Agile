import json
from datetime import datetime
from typing import Dict, Any, Tuple, Optional
from pydantic import TypeAdapter
from src.core.logger import logger
from src.services.transaction_service import TransactionService
from src.db.crud import crud_recurrence, crud_user
from src.db.schemas import transaction as transaction_schema
from src.db.schemas import recurrent as recurrent_schema
from src.tools.base import BaseTool
from src.utils.enums import RecurrenceFrequency


class RecurrenceTool(BaseTool):
    """
    Tool to create a Recurrent Transaction.
    It creates a BASE transaction (prototype) and then the Recurrence Rule.
    """
    name = "recurrence"

    def __init__(self, service: TransactionService, db_session):
        self.service = service
        self.db = db_session

    @property
    def schema(self) -> Dict[str, Any]:
        categories = self.service.get_all_category_names()
        return {
            "type": "object",
            "properties": {
                "amount": {"type": "integer", "description": "Amount in CENTS"},
                "description": {"type": "string"},
                "category_name": {"type": "string", "enum": categories},
                "transaction_type": {"type": "string", "enum": ["expense", "income"]},
                "day_of_month": {"type": "integer", "minimum": 1, "maximum": 31},
                "is_salary": {"type": "boolean", "description": "If true, updates user salary link"}
            },
            "required": ["amount", "description", "transaction_type", "day_of_month"]
        }

    def get_extraction_prompt(self, message: str, partial: Optional[Dict[str, Any]] = None) -> str:
        categories = self.service.get_all_category_names()
        cat_list = "\n".join(f"  - {cat}" for cat in categories)
        partial_str = f"\nPrevious data: {json.dumps(partial)}" if partial else ""

        return f"""Extract RECURRENCE/SUBSCRIPTION data.
        User: "{message}"{partial_str}
        
        AVAILABLE CATEGORIES:
        {cat_list}

        SCHEMA:
        - amount (int cents)
        - description (string)
        - transaction_type (expense/income)
        - day_of_month (int 1-31): The day it repeats.
        - category_name (string): Required for expenses.
        - is_salary (bool): True if user says "This is my salary" or "My monthly income".

        NOTE: If user says "every month on the 5th", day_of_month is 5.
        
        Output JSON only.
        """

    def execute(self, params: Dict[str, Any], user_id: int) -> Tuple[str, str]:
        logger.info(f"Tool Executing: Recurrence", extra={"payload": params})
        tx_type = params["transaction_type"]
        is_salary = params.pop("is_salary", False)
        day = params.pop("day_of_month")
        today = datetime.now()
        ref_date = today.date().replace(day=min(day, 28))
        params["reference_date"] = ref_date
        if tx_type == "expense":
            cat_name = params.pop("category_name", None)
            if cat_name:
                category = self.service.get_category_by_name(cat_name)
                if category:
                    params["category_id"] = category.id
        else:
            params["category_id"] = None
        adapter = TypeAdapter(transaction_schema.TransactionCreate)
        validated_tx = adapter.validate_python(params)
        base_tx = self.service.create_transaction(user_id=user_id, transaction_data=validated_tx)
        recurrence_data = recurrent_schema.RecurrentTransactionCreate(
            base_transaction_id=base_tx.id,
            recurrence_day=day,
            frequency=RecurrenceFrequency.MONTHLY
        )
        recurrence = crud_recurrence.create_recurrence(self.db, recurrence_data, user_id)
        if is_salary and tx_type == "income":
            user = crud_user.get_user(self.db, user_id)
            user.salary_recurrence_id = recurrence.id
            self.db.add(user)
            self.db.commit()

        return (
            f"Recurrence created: {base_tx.description} (R$ {base_tx.amount/100:.2f}) monthly on day {day}.",
            "Created Recurrence Rule"
        )