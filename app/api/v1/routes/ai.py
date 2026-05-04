from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
from typing import Optional
from app.database import get_db
from app.schemas.common import APIResponse
from app.schemas.ai import AIQueryRequest, AIAnalysisRequest
from app.services.ai_service import AIService
from app.services.analysis_service import AnalysisService
from app.services.budget_service import BudgetService
from app.repositories.expense_repository import ExpenseRepository
from app.repositories.budget_repository import BudgetRepository
from app.core.security import get_current_user_id

router = APIRouter(prefix="/ai")


def get_ai_service(db: AsyncSession = Depends(get_db)) -> AIService:
    expense_repo = ExpenseRepository(db)
    budget_repo = BudgetRepository(db)
    analysis_service = AnalysisService(expense_repo)
    budget_service = BudgetService(budget_repo, expense_repo)
    return AIService(analysis_service, budget_service)


@router.post("/analyze/{user_id}", response_model=APIResponse)
async def analyze_spending(
    user_id: str,
    payload: AIAnalysisRequest,
    _current_user: str = Depends(get_current_user_id),
    ai_service: AIService = Depends(get_ai_service),
):
    start = date.fromisoformat(payload.date_range_start) if payload.date_range_start else date.today().replace(day=1)
    end = date.fromisoformat(payload.date_range_end) if payload.date_range_end else date.today()
    result = await ai_service.analyze(user_id, start, end, payload.include_recommendations)
    return APIResponse.ok(data=result.model_dump(), message="Analysis completed")


@router.post("/query/{user_id}", response_model=APIResponse)
async def query(
    user_id: str,
    payload: AIQueryRequest,
    _current_user: str = Depends(get_current_user_id),
    ai_service: AIService = Depends(get_ai_service),
):
    result = await ai_service.query(user_id, payload.query, payload.context)
    return APIResponse.ok(data=result.model_dump(), message="Query processed")


@router.get("/daily-digest/{user_id}", response_model=APIResponse)
async def daily_digest(
    user_id: str,
    _current_user: str = Depends(get_current_user_id),
    ai_service: AIService = Depends(get_ai_service),
):
    result = await ai_service.get_daily_digest(user_id)
    return APIResponse.ok(data=result.model_dump(), message="Daily digest generated")


@router.get("/alerts/{user_id}", response_model=APIResponse)
async def get_alerts(
    user_id: str,
    _current_user: str = Depends(get_current_user_id),
    ai_service: AIService = Depends(get_ai_service),
):
    alerts = await ai_service.get_alerts(user_id)
    return APIResponse.ok(data=[a.model_dump() for a in alerts], message="Alerts retrieved")


@router.post("/recommendations/{user_id}", response_model=APIResponse)
async def get_recommendations(
    user_id: str,
    _current_user: str = Depends(get_current_user_id),
    ai_service: AIService = Depends(get_ai_service),
):
    recs = await ai_service.get_recommendations(user_id)
    return APIResponse.ok(data={"recommendations": recs}, message="Recommendations generated")
