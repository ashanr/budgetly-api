from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime, date


class ReportSummary(BaseModel):
    period_start: date
    period_end: date
    total_expenses: float
    total_income: float
    net_savings: float
    expense_count: int
    top_categories: list[dict]
    budget_adherence: float
    generated_at: datetime


class MonthlyReport(BaseModel):
    year: int
    month: int
    daily_breakdown: list[dict]
    category_breakdown: list[dict]
    total_expenses: float
    vs_previous_month: float
    insights: list[str]
    generated_at: datetime


class ForecastReport(BaseModel):
    current_month_projection: float
    year_end_projection: float
    monthly_average: float
    savings_potential: float
    trend: str
    scenarios: list[dict]
    generated_at: datetime
