from pydantic import BaseModel

class DashboardSummary(BaseModel):
    total_balance: int
    total_income: int
    total_expense: int
    total_savings: int
    income_change_pct: float
    expense_change_pct: float
    savings_change_pct: float

class CategorySpending(BaseModel):
    category_name: str
    amount: int
    percentage: float

class MonthlyEvolution(BaseModel):
    month: str
    total_income: int
    total_expense: int
    balance: int