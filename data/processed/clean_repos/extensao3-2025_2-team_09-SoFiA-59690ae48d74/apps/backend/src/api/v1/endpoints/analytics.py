from typing import List, Optional
from fastapi import APIRouter, Depends, status, Query
from src.api.deps import get_analytics_service
from src.services.analytics_service import AnalyticsService
from src.db.schemas import analytics as analytics_schema

router = APIRouter()

@router.get(
    "/summary",
    response_model=analytics_schema.DashboardSummary,
    status_code=status.HTTP_200_OK,
)
def get_dashboard_summary(
        month: Optional[int] = Query(None, ge=1, le=12),
        year: Optional[int] = Query(None),
        service: AnalyticsService = Depends(get_analytics_service)
):
    """
    Returns summary cards.
    If month/year are provided, calculates for that specific period.
    Otherwise, defaults to current month.
    """
    return service.get_summary_cards(month=month, year=year)


@router.get(
    "/spending-by-category",
    response_model=List[analytics_schema.CategorySpending],
    status_code=status.HTTP_200_OK,
)
def get_spending_by_category(
        month: Optional[int] = Query(None, ge=1, le=12),
        year: Optional[int] = Query(None),
        service: AnalyticsService = Depends(get_analytics_service)
):
    return service.get_spending_by_category(month=month, year=year)


@router.get(
    "/monthly-evolution",
    response_model=List[analytics_schema.MonthlyEvolution],
    status_code=status.HTTP_200_OK,
)
def get_monthly_evolution(
        months: int = 6,
        service: AnalyticsService = Depends(get_analytics_service)
):
    return service.get_monthly_evolution(months=months)