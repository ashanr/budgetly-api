from decimal import Decimal
from datetime import date, timedelta
from collections import defaultdict
from app.repositories.expense_repository import ExpenseRepository


class AnalysisService:
    def __init__(self, expense_repo: ExpenseRepository):
        self.expense_repo = expense_repo

    async def analyze_spending(self, user_id: str, start: date, end: date) -> dict:
        expenses = await self.expense_repo.get_by_date_range(user_id, start, end)

        total_spent = sum(float(e.amount) for e in expenses)
        by_category: dict[str, float] = defaultdict(float)
        by_merchant: dict[str, float] = defaultdict(float)
        recurring_total = 0.0

        for e in expenses:
            cat = e.category_id or "Uncategorized"
            by_category[cat] += float(e.amount)
            if e.merchant:
                by_merchant[e.merchant] += float(e.amount)
            if e.is_recurring:
                recurring_total += float(e.amount)

        top_merchants = sorted(
            [{"merchant": k, "total": v} for k, v in by_merchant.items()],
            key=lambda x: x["total"],
            reverse=True,
        )[:5]

        avg = total_spent / len(expenses) if expenses else 0
        anomalies = [
            {"id": e.id, "amount": float(e.amount), "date": str(e.expense_date), "description": e.description}
            for e in expenses
            if float(e.amount) > avg * 3 and avg > 0
        ]

        return {
            "total_spent": total_spent,
            "by_category": dict(by_category),
            "top_merchants": top_merchants,
            "recurring_total": recurring_total,
            "anomalies": anomalies,
            "expense_count": len(expenses),
        }

    async def get_monthly_breakdown(self, user_id: str, year: int, month: int) -> dict:
        start = date(year, month, 1)
        if month == 12:
            end = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end = date(year, month + 1, 1) - timedelta(days=1)

        expenses = await self.expense_repo.get_by_date_range(user_id, start, end)

        daily: dict[str, float] = defaultdict(float)
        by_category: dict[str, float] = defaultdict(float)

        for e in expenses:
            daily[str(e.expense_date)] += float(e.amount)
            cat = e.category_id or "Uncategorized"
            by_category[cat] += float(e.amount)

        return {
            "daily_breakdown": [{"date": k, "total": v} for k, v in sorted(daily.items())],
            "category_breakdown": [{"category": k, "total": v} for k, v in sorted(by_category.items(), key=lambda x: x[1], reverse=True)],
            "total_expenses": sum(float(e.amount) for e in expenses),
        }

    def _calculate_trend(self, months_data: list[float], monthly_avg: float) -> str:
        if len(set(round(m, -2) for m in months_data)) <= 1:
            return "stable"
        # months_data[0] is the most recent month; months_data[-1] is the oldest
        if len(months_data) >= 2 and months_data[0] > months_data[-1]:
            return "increasing"
        return "decreasing"

    async def forecast_spending(self, user_id: str) -> dict:
        today = date.today()
        months_data = []
        for i in range(1, 4):
            month = today.month - i
            year = today.year
            while month <= 0:
                month += 12
                year -= 1
            total = await self.expense_repo.get_total_by_user_month(user_id, year, month)
            months_data.append(float(total))

        monthly_avg = sum(months_data) / len(months_data) if months_data else 0
        current_month_projection = monthly_avg

        return {
            "monthly_average": monthly_avg,
            "current_month_projection": current_month_projection,
            "year_end_projection": monthly_avg * 12,
            "savings_potential": max(0, monthly_avg * 0.15),
            "trend": self._calculate_trend(months_data, monthly_avg),
        }
