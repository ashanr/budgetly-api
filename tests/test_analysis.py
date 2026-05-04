import pytest
from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock
from app.services.analysis_service import AnalysisService
from app.models.expense import Expense


def make_expense(amount: float, category_id: str = "food", merchant: str = "Shop", is_recurring: bool = False) -> Expense:
    e = MagicMock(spec=Expense)
    e.amount = Decimal(str(amount))
    e.category_id = category_id
    e.merchant = merchant
    e.is_recurring = is_recurring
    e.expense_date = date.today()
    e.id = "test-id"
    e.description = "test"
    return e


@pytest.mark.asyncio
async def test_analyze_spending_empty():
    mock_repo = AsyncMock()
    mock_repo.get_by_date_range.return_value = []
    service = AnalysisService(mock_repo)
    result = await service.analyze_spending("user1", date.today(), date.today())
    assert result["total_spent"] == 0.0
    assert result["expense_count"] == 0


@pytest.mark.asyncio
async def test_analyze_spending_with_data():
    mock_repo = AsyncMock()
    mock_repo.get_by_date_range.return_value = [
        make_expense(100.0, "food"),
        make_expense(50.0, "transport"),
        make_expense(200.0, "food", is_recurring=True),
    ]
    service = AnalysisService(mock_repo)
    result = await service.analyze_spending("user1", date.today(), date.today())
    assert result["total_spent"] == 350.0
    assert result["by_category"]["food"] == 300.0
    assert result["recurring_total"] == 200.0


@pytest.mark.asyncio
async def test_anomaly_detection():
    mock_repo = AsyncMock()
    expenses = [make_expense(10.0) for _ in range(10)]
    expenses.append(make_expense(1000.0))  # anomaly
    mock_repo.get_by_date_range.return_value = expenses
    service = AnalysisService(mock_repo)
    result = await service.analyze_spending("user1", date.today(), date.today())
    assert len(result["anomalies"]) >= 1


@pytest.mark.asyncio
async def test_monthly_breakdown():
    mock_repo = AsyncMock()
    mock_repo.get_by_date_range.return_value = [
        make_expense(100.0, "food"),
        make_expense(50.0, "transport"),
    ]
    service = AnalysisService(mock_repo)
    result = await service.get_monthly_breakdown("user1", 2026, 1)
    assert result["total_expenses"] == 150.0
    assert len(result["category_breakdown"]) == 2
