from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime


class AIQueryRequest(BaseModel):
    query: str
    context: Optional[dict] = None
    date_range_start: Optional[str] = None
    date_range_end: Optional[str] = None


class AIAnalysisRequest(BaseModel):
    date_range_start: Optional[str] = None
    date_range_end: Optional[str] = None
    include_recommendations: bool = True


class SpendingAnalysis(BaseModel):
    total_spent: float
    by_category: dict[str, float]
    top_merchants: list[dict]
    recurring_total: float
    period_comparison: Optional[dict] = None
    anomalies: list[dict]
    summary: str
    recommendations: list[str]


class AIQueryResponse(BaseModel):
    query: str
    answer: str
    data: Optional[Any] = None
    confidence: float
    timestamp: datetime


class Alert(BaseModel):
    alert_id: str
    type: str
    severity: str
    title: str
    message: str
    data: Optional[dict] = None
    created_at: datetime


class DailyDigest(BaseModel):
    date: str
    total_spent_today: float
    total_spent_month: float
    budget_status: list[dict]
    top_category: Optional[str] = None
    insights: list[str]
    alerts: list[Alert]
