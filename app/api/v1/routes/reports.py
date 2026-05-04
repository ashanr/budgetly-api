from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, datetime, timezone
from typing import Optional
from app.database import get_db
from app.schemas.common import APIResponse
from app.schemas.report import ReportSummary, MonthlyReport, ForecastReport
from app.services.analysis_service import AnalysisService
from app.repositories.expense_repository import ExpenseRepository
from app.core.security import get_current_user_id

router = APIRouter(prefix="/reports")


def get_analysis_service(db: AsyncSession = Depends(get_db)) -> AnalysisService:
    return AnalysisService(ExpenseRepository(db))


@router.get("/summary/{user_id}", response_model=APIResponse)
async def get_summary(
    user_id: str,
    start: Optional[date] = Query(default=None),
    end: Optional[date] = Query(default=None),
    _current_user: str = Depends(get_current_user_id),
    analysis_service: AnalysisService = Depends(get_analysis_service),
):
    period_start = start or date.today().replace(day=1)
    period_end = end or date.today()
    data = await analysis_service.analyze_spending(user_id, period_start, period_end)

    summary = ReportSummary(
        period_start=period_start,
        period_end=period_end,
        total_expenses=data["total_spent"],
        total_income=0.0,
        net_savings=0.0,
        expense_count=data["expense_count"],
        top_categories=[{"category": k, "total": v} for k, v in sorted(data["by_category"].items(), key=lambda x: x[1], reverse=True)[:5]],
        budget_adherence=100.0,
        generated_at=datetime.now(timezone.utc),
    )
    return APIResponse.ok(data=summary.model_dump(), message="Summary report generated")


@router.get("/monthly/{user_id}", response_model=APIResponse)
async def get_monthly(
    user_id: str,
    year: int = Query(default=None),
    month: int = Query(default=None),
    _current_user: str = Depends(get_current_user_id),
    analysis_service: AnalysisService = Depends(get_analysis_service),
):
    today = date.today()
    y = year or today.year
    m = month or today.month
    data = await analysis_service.get_monthly_breakdown(user_id, y, m)

    report = MonthlyReport(
        year=y,
        month=m,
        daily_breakdown=data["daily_breakdown"],
        category_breakdown=data["category_breakdown"],
        total_expenses=data["total_expenses"],
        vs_previous_month=0.0,
        insights=[],
        generated_at=datetime.now(timezone.utc),
    )
    return APIResponse.ok(data=report.model_dump(), message="Monthly report generated")


@router.get("/category/{user_id}", response_model=APIResponse)
async def get_category_report(
    user_id: str,
    start: Optional[date] = Query(default=None),
    end: Optional[date] = Query(default=None),
    _current_user: str = Depends(get_current_user_id),
    analysis_service: AnalysisService = Depends(get_analysis_service),
):
    period_start = start or date.today().replace(day=1)
    period_end = end or date.today()
    data = await analysis_service.analyze_spending(user_id, period_start, period_end)
    return APIResponse.ok(
        data={
            "by_category": data["by_category"],
            "period_start": str(period_start),
            "period_end": str(period_end),
        },
        message="Category report generated",
    )


@router.get("/forecast/{user_id}", response_model=APIResponse)
async def get_forecast(
    user_id: str,
    _current_user: str = Depends(get_current_user_id),
    analysis_service: AnalysisService = Depends(get_analysis_service),
):
    data = await analysis_service.forecast_spending(user_id)
    forecast = ForecastReport(
        current_month_projection=data["current_month_projection"],
        year_end_projection=data["year_end_projection"],
        monthly_average=data["monthly_average"],
        savings_potential=data["savings_potential"],
        trend=data["trend"],
        scenarios=[
            {"name": "conservative", "projection": data["monthly_average"] * 12 * 0.9},
            {"name": "base", "projection": data["year_end_projection"]},
            {"name": "optimistic", "projection": data["monthly_average"] * 12 * 1.1},
        ],
        generated_at=datetime.now(timezone.utc),
    )
    return APIResponse.ok(data=forecast.model_dump(), message="Forecast report generated")
