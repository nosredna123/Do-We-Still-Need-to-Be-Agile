# /home/yordle/IdeaProjects/SoFiA/apps/backend/src/tools/finance.py

import json
from datetime import datetime
from typing import Dict, Any, Tuple, Optional, List
from pydantic import TypeAdapter
from src.core.logger import logger
from src.services.transaction_service import TransactionService
from src.tools.base import BaseTool
from src.utils.enums import UserIntent
from src.db.schemas import transaction as transaction_schema


class ExpenseTool(BaseTool):
    name = "expense"
    def __init__(self, service: TransactionService):
        self.service = service

    @property
    def schema(self) -> Dict[str, Any]:
        categories = self.service.get_all_category_names()
        return {
            "type": "object",
            "properties": {
                "amount": {"type": "integer", "description": "Amount in CENTS"},
                "description": {"type": "string"},
                "category_name": {"type": "string", "enum": categories},
                "reference_date": {
                    "type": "string",
                    "format": "date",
                    "description": "YYYY-MM-DD. Use 1st of month if day unknown."
                }
            },
            "required": ["amount", "description"]
        }

    @property
    def required_fields(self) -> List[str]:
        return ["amount", "description", "category_name"]

    def get_extraction_prompt(self, message: str, partial: Optional[Dict[str, Any]] = None) -> str:
        categories = self.service.get_all_category_names()
        cat_list = "\n".join(f"  - {cat}" for cat in categories)
        partial_json = json.dumps(partial) if partial else "{}"
        today_str = datetime.now().strftime("%Y-%m-%d")
        return f"""You are a strict data extraction engine.
        TODAY: {today_str}
        CURRENT DATA (Merge with this): {partial_json}
        USER MESSAGE: "{message}"
        AVAILABLE CATEGORIES:
        {cat_list}
        RULES:
        1. Extract 'amount' in CENTS (multiply by 100). E.g., "60 reais" -> 6000.
        2. Extract 'description' if stated.
        3. CATEGORY RULE: If the user message matches or matches closely one of the AVAILABLE CATEGORIES, extract 'category_name'.
        4. DATE RULE: Extract 'reference_date' (YYYY-MM-DD) based on the user's text relative to TODAY. 
           - E.g. "mês passado" (last month), "ontem" (yesterday), "dia 5" (day 5 of current month).
           - If no date is mentioned, omit 'reference_date'.

        IMPORTANT: If the user provides a category, do NOT overwrite the 'description' unless explicitly changed.

        Output JSON only.
        """

    def execute(self, params: Dict[str, Any], user_id: int) -> Tuple[str, str]:
        params["transaction_type"] = "expense"
        logger.info(f"Tool Executing: Expense", extra={"payload": params})

        cat_name = params.pop("category_name", None)
        if cat_name:
            category = self.service.get_category_by_name(cat_name)
            if category:
                params["category_id"] = category.id

        adapter = TypeAdapter(transaction_schema.TransactionCreate)
        validated_data = adapter.validate_python(params)
        tx = self.service.create_transaction(user_id=user_id, transaction_data=validated_data)
        date_str = tx.reference_date.strftime("%B %Y")
        return (
            f"Expense created: {tx.description} (R$ {tx.amount / 100:.2f}) in {date_str}",
            f"Created Expense: {tx.description}"
        )


class IncomeTool(BaseTool):
    name = "income"
    def __init__(self, service: TransactionService):
        self.service = service

    @property
    def schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "amount": {"type": "integer"},
                "description": {"type": "string"},
                "reference_date": {
                    "type": "string",
                    "format": "date",
                    "description": "YYYY-MM-DD. Use 1st of month if day unknown."
                }
            },
            "required": ["amount", "description"]
        }

    @property
    def required_fields(self) -> List[str]:
        return ["amount", "description"]

    def get_extraction_prompt(self, message: str, partial: Optional[Dict[str, Any]] = None) -> str:
        partial_json = json.dumps(partial) if partial else "{}"
        today_str = datetime.now().strftime("%Y-%m-%d")

        return f"""Extract INCOME data. 
        TODAY: {today_str}
        CURRENT DATA: {partial_json}
        User: "{message}"
        
        Schema: 
        - amount (int cents). Convert "60 reais" -> 6000.
        - description (string)
        - reference_date (YYYY-MM-DD): Handle relative dates.
        
        Extract known fields. Omit unknown. No JSON markdown."""

    def execute(self, params: Dict[str, Any], user_id: int) -> Tuple[str, str]:
        params["transaction_type"] = "income"
        params["category_id"] = None
        logger.info(f"Tool Executing: Income", extra={"payload": params})
        adapter = TypeAdapter(transaction_schema.TransactionCreate)
        validated_data = adapter.validate_python(params)
        tx = self.service.create_transaction(user_id=user_id, transaction_data=validated_data)

        date_str = tx.reference_date.strftime("%B %Y")
        return (
            f"Income created: {tx.description} (R$ {tx.amount / 100:.2f}) in {date_str}",
            f"Created Income: {tx.description}"
        )


class QueryTool(BaseTool):
    """Smart Query Tool that filters transactions."""
    def __init__(self, service: TransactionService):
        self.service = service

    @property
    def name(self) -> str:
        return UserIntent.QUERY.value

    @property
    def schema(self) -> Dict[str, Any]:
        categories = self.service.get_all_category_names()
        return {
            "type": "object",
            "properties": {
                "start_date": {"type": "string", "format": "date", "description": "YYYY-MM-DD"},
                "end_date": {"type": "string", "format": "date", "description": "YYYY-MM-DD"},
                "category_name": {"type": "string", "enum": categories},
                "limit": {"type": "integer"},
                "transaction_type": {"type": "string", "enum": ["expense", "income"]}
            },
            "required": []
        }

    @property
    def required_fields(self) -> List[str]:
        return []

    def get_extraction_prompt(self, message: str, partial: Optional[Dict[str, Any]] = None) -> str:
        today = datetime.now().strftime("%Y-%m-%d")
        categories = self.service.get_all_category_names()
        cat_list = "\n".join(f"  - {cat}" for cat in categories)
        partial_json = json.dumps(partial) if partial else "{}"

        return f"""You are a query parser for a finance DB.
        TODAY IS: {today}
        CURRENT FILTERS: {partial_json}
        USER QUERY: "{message}"

        AVAILABLE CATEGORIES (Exact match required):
        {cat_list}

        YOUR TASK: Convert natural language requirements into JSON filters.

        FIELDS:
        - start_date (YYYY-MM-DD): derived from "this month", "last week", "in January".
        - end_date (YYYY-MM-DD): derived from "until now", "yesterday", end of month.
        - category_name (string): MUST be one of the available categories. Only set if explicitly requested.
        - transaction_type (string): 'expense' or 'income' if specified.

        EXAMPLES:
        "How much spent on Food this month?" -> {{"start_date": "2024-05-01", "end_date": "2024-05-31", "category_name": "Alimentação", "transaction_type": "expense"}}
        "Total spent in January" -> {{"start_date": "2024-01-01", "end_date": "2024-01-31", "transaction_type": "expense"}}

        OUTPUT VALID JSON ONLY. Omit keys if not mentioned.
        """

    def execute(self, params: Dict[str, Any], user_id: int) -> Tuple[str, str]:
        logger.info(f"QueryTool executing with params: {json.dumps(params, ensure_ascii=False)}")
        filters = {}
        if "start_date" in params:
            try:
                filters["date_from"] = datetime.strptime(params["start_date"], "%Y-%m-%d").date()
            except ValueError:
                logger.warning(f"Invalid start_date format: {params['start_date']}")

        if "end_date" in params:
            try:
                filters["date_to"] = datetime.strptime(params["end_date"], "%Y-%m-%d").date()
            except ValueError:
                logger.warning(f"Invalid end_date format: {params['end_date']}")
        if "transaction_type" in params: filters["transaction_type"] = params["transaction_type"]
        cat_name = params.get("category_name")
        if cat_name:
            category = self.service.get_category_by_name(cat_name)
            if category:
                filters["category_id"] = category.id
                logger.info(f"Mapped category '{cat_name}' to ID {category.id}")
        logger.info(f"🔎 DB Filters: {filters}")
        results = self.service.get_transactions(filters=filters)
        if not results:
            return "No transactions found matching those criteria.", "Query (0 results)"
        total_cents = sum(t.amount for t in results)
        total_reais = total_cents / 100.0
        summary_lines = []
        for tx in results:
            summary_lines.append(f"- {tx.reference_date.strftime('%d/%m')}: {tx.description} (R$ {tx.amount / 100:.2f})")
        full_text = (
                f"Found {len(results)} transactions. "
                f"Total Sum: R$ {total_reais:.2f} (exact value: {total_reais} BRL).\n"
                f"Details:\n" + "\n".join(summary_lines)
        )
        return full_text, f"Query ({len(results)} results)"