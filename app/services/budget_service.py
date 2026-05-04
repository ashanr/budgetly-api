from datetime import date
from decimal import Decimal
from app.repositories.budget_repository import BudgetRepository
from app.repositories.expense_repository import ExpenseRepository
from app.schemas.budget import BudgetHealth


class BudgetService:
    def __init__(self, budget_repo: BudgetRepository, expense_repo: ExpenseRepository):
        self.budget_repo = budget_repo
        self.expense_repo = expense_repo

    async def get_budget_health(self, user_id: str) -> list[BudgetHealth]:
        budgets = await self.budget_repo.get_active_budgets(user_id)
        today = date.today()
        results = []

        for budget in budgets:
            start = budget.start_date
            end = budget.end_date or today
            expenses = await self.expense_repo.get_by_date_range(user_id, start, end)

            if budget.category_id:
                expenses = [e for e in expenses if e.category_id == budget.category_id]

            spent = sum(float(e.amount) for e in expenses)
            allocated = float(budget.amount)
            remaining = allocated - spent
            utilization = (spent / allocated * 100) if allocated > 0 else 0

            if utilization >= 100:
                status = "over_budget"
                health_score = 0.0
            elif utilization >= budget.alert_threshold:
                status = "warning"
                health_score = max(0, (100 - utilization) / (100 - budget.alert_threshold) * 50)
            else:
                status = "healthy"
                health_score = 100 - utilization

            results.append(BudgetHealth(
                budget_id=budget.id,
                name=budget.name,
                allocated=Decimal(str(allocated)),
                spent=Decimal(str(spent)),
                remaining=Decimal(str(remaining)),
                utilization_percent=round(utilization, 2),
                health_score=round(health_score, 2),
                status=status,
                is_over_budget=spent > allocated,
            ))

        return results

    async def get_alerts(self, user_id: str) -> list[dict]:
        health_list = await self.get_budget_health(user_id)
        alerts = []
        for h in health_list:
            if h.is_over_budget:
                alerts.append({
                    "type": "over_budget",
                    "severity": "high",
                    "budget_name": h.name,
                    "message": f"You have exceeded your {h.name} budget by {abs(float(h.remaining)):.2f}",
                })
            elif h.status == "warning":
                alerts.append({
                    "type": "budget_warning",
                    "severity": "medium",
                    "budget_name": h.name,
                    "message": f"You have used {h.utilization_percent:.1f}% of your {h.name} budget",
                })
        return alerts
