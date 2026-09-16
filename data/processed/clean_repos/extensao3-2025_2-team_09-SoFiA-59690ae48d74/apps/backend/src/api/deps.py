from typing import Generator, List
from fastapi import Depends
from sqlalchemy.orm import Session

from src import db
from src.db.database.connection import get_db
from src.services.analytics_service import AnalyticsService
from src.services.chat_service import ChatService
from src.services.transaction_service import TransactionService
from src.tools.base import BaseTool
from src.tools.finance import ExpenseTool, IncomeTool, QueryTool
from src.tools.recurrence import RecurrenceTool

def get_transaction_service(db: Session = Depends(get_db)) -> TransactionService:
    return TransactionService(db)

def get_tools(
        transaction_service: TransactionService = Depends(get_transaction_service)
) -> List[BaseTool]:
    """
    Registry of all available tools.
    If you add a 'DeleteTool' later, you just add it to this list.
    """
    return [
        ExpenseTool(transaction_service),
        IncomeTool(transaction_service),
        QueryTool(transaction_service),
        RecurrenceTool(transaction_service, db)
    ]

def get_chat_service(
    db: Session = Depends(get_db),
    tools: List[BaseTool] = Depends(get_tools)
) -> ChatService:
    return ChatService(db=db, tools=tools)

def get_analytics_service(db: Session = Depends(get_db)) -> AnalyticsService:
    return AnalyticsService(db)