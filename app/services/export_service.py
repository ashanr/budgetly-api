import csv
import io
from datetime import date
from typing import Optional
from app.repositories.expense_repository import ExpenseRepository
from app.repositories.budget_repository import BudgetRepository


class ExportService:
    def __init__(self, expense_repo: ExpenseRepository, budget_repo: BudgetRepository):
        self.expense_repo = expense_repo
        self.budget_repo = budget_repo

    async def export_csv(self, user_id: str, start: Optional[date] = None, end: Optional[date] = None) -> str:
        if start and end:
            expenses = await self.expense_repo.get_by_date_range(user_id, start, end)
        else:
            expenses = await self.expense_repo.get_by_user(user_id)

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=["id", "date", "amount", "currency", "category", "merchant", "description", "recurring"])
        writer.writeheader()
        for e in expenses:
            writer.writerow({
                "id": e.id,
                "date": str(e.expense_date),
                "amount": str(e.amount),
                "currency": e.currency,
                "category": e.category_id or "",
                "merchant": e.merchant or "",
                "description": e.description or "",
                "recurring": str(e.is_recurring),
            })
        return output.getvalue()

    async def export_json(self, user_id: str, start: Optional[date] = None, end: Optional[date] = None) -> dict:
        if start and end:
            expenses = await self.expense_repo.get_by_date_range(user_id, start, end)
        else:
            expenses = await self.expense_repo.get_by_user(user_id)

        budgets = await self.budget_repo.get_by_user(user_id)

        return {
            "user_id": user_id,
            "exported_at": str(date.today()),
            "expenses": [
                {
                    "id": e.id,
                    "date": str(e.expense_date),
                    "amount": str(e.amount),
                    "currency": e.currency,
                    "category_id": e.category_id,
                    "merchant": e.merchant,
                    "description": e.description,
                    "is_recurring": e.is_recurring,
                    "tags": e.tags,
                }
                for e in expenses
            ],
            "budgets": [
                {
                    "id": b.id,
                    "name": b.name,
                    "amount": str(b.amount),
                    "currency": b.currency,
                    "period": b.period,
                    "start_date": str(b.start_date),
                    "end_date": str(b.end_date) if b.end_date else None,
                }
                for b in budgets
            ],
        }

    async def backup(self, user_id: str) -> dict:
        return await self.export_json(user_id)

    async def restore(self, user_id: str, backup_data: dict) -> dict:
        expense_count = len(backup_data.get("expenses", []))
        budget_count = len(backup_data.get("budgets", []))
        return {
            "restored_expenses": expense_count,
            "restored_budgets": budget_count,
            "status": "preview_only",
            "message": "Restore preview completed. Full restore requires additional confirmation.",
        }
