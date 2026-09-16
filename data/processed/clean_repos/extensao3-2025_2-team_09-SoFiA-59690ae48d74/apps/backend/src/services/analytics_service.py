import datetime
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from src.db.models.models import Transaction, Category, User
from src.utils.enums import TransactionType
from src.db.schemas import analytics as schemas
from src.utils.constants import APPLICATION_USER_ID

class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db
        self.user_id = APPLICATION_USER_ID

    def _get_month_range(self, year: int, month: int):
        """Helper to get start and end date of a specific month."""
        start_date = datetime.date(year, month, 1)
        if month == 12:
            end_date = datetime.date(year + 1, 1, 1) - datetime.timedelta(days=1)
        else:
            end_date = datetime.date(year, month + 1, 1) - datetime.timedelta(days=1)
        return start_date, end_date

    def get_summary_cards(self, month: Optional[int] = None, year: Optional[int] = None) -> schemas.DashboardSummary:
        today = datetime.date.today()
        target_month = month or today.month
        target_year = year or today.year
        curr_start, curr_end = self._get_month_range(target_year, target_month)
        first_of_curr = datetime.date(target_year, target_month, 1)
        last_month_date = first_of_curr - datetime.timedelta(days=1)
        prev_start, prev_end = self._get_month_range(last_month_date.year, last_month_date.month)

        def get_sum(start, end, tx_type):
            return self.db.query(func.sum(Transaction.amount)).filter(
                Transaction.user_id == self.user_id,
                Transaction.reference_date >= start,
                Transaction.reference_date <= end,
                Transaction.transaction_type == tx_type
            ).scalar() or 0

        curr_income = get_sum(curr_start, curr_end, TransactionType.INCOME)
        curr_expense = get_sum(curr_start, curr_end, TransactionType.EXPENSE)
        prev_income = get_sum(prev_start, prev_end, TransactionType.INCOME)
        prev_expense = get_sum(prev_start, prev_end, TransactionType.EXPENSE)
        curr_savings = curr_income - curr_expense
        prev_savings = prev_income - prev_expense
        total_income_lifetime = self.db.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == self.user_id,
            Transaction.transaction_type == TransactionType.INCOME
        ).scalar() or 0
        total_expense_lifetime = self.db.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == self.user_id,
            Transaction.transaction_type == TransactionType.EXPENSE
        ).scalar() or 0
        total_balance = total_income_lifetime - total_expense_lifetime
        def calc_change(curr, prev):
            if prev == 0:
                return 100.0 if curr > 0 else 0.0
            return ((curr - prev) / prev) * 100

        return schemas.DashboardSummary(
            total_balance=total_balance,
            total_income=curr_income,
            total_expense=curr_expense,
            total_savings=curr_savings,
            income_change_pct=calc_change(curr_income, prev_income),
            expense_change_pct=calc_change(curr_expense, prev_expense),
            savings_change_pct=calc_change(curr_savings, prev_savings)
        )

    def get_spending_by_category(self, month: Optional[int] = None, year: Optional[int] = None) -> list[schemas.CategorySpending]:
        today = datetime.date.today()
        target_month = month or today.month
        target_year = year or today.year
        start_date, end_date = self._get_month_range(target_year, target_month)
        results = (
            self.db.query(
                Category.name,
                func.sum(Transaction.amount).label("total")
            )
            .join(Category, Transaction.category_id == Category.id)
            .filter(
                Transaction.user_id == self.user_id,
                Transaction.transaction_type == TransactionType.EXPENSE,
                Transaction.reference_date >= start_date,
                Transaction.reference_date <= end_date
            )
            .group_by(Category.name)
            .all()
        )

        total_expense_month = sum(r.total for r in results) or 1
        data = []
        for cat_name, total_amount in results:
            data.append(schemas.CategorySpending(
                category_name=cat_name,
                amount=total_amount,
                percentage=round((total_amount / total_expense_month) * 100, 2)
            ))

        return sorted(data, key=lambda x: x.amount, reverse=True)

    def get_monthly_evolution(self, months: int = 6) -> list[schemas.MonthlyEvolution]:
        end_date = datetime.date.today()
        start_date = (end_date.replace(day=1) - datetime.timedelta(days=30 * months)).replace(day=1)
        query = (
            self.db.query(
                func.strftime("%Y-%m", Transaction.reference_date).label("month_str"),
                func.sum(case((Transaction.transaction_type == TransactionType.INCOME, Transaction.amount), else_=0)).label("income"),
                func.sum(case((Transaction.transaction_type == TransactionType.EXPENSE, Transaction.amount), else_=0)).label("expense"),
            )
            .filter(
                Transaction.user_id == self.user_id,
                Transaction.reference_date >= start_date
            )
            .group_by("month_str")
            .order_by("month_str")
        )

        results = query.all()
        data = []
        for r in results:
            data.append(schemas.MonthlyEvolution(
                month=r.month_str,
                total_income=r.income or 0,
                total_expense=r.expense or 0,
                balance=(r.income or 0) - (r.expense or 0)
            ))

        return data