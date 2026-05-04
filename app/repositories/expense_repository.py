from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from datetime import date
from decimal import Decimal
from app.models.expense import Expense


class ExpenseRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, expense_id: str) -> Optional[Expense]:
        result = await self.db.execute(select(Expense).where(Expense.id == expense_id))
        return result.scalar_one_or_none()

    async def get_by_user(self, user_id: str, limit: int = 100, offset: int = 0) -> list[Expense]:
        result = await self.db.execute(
            select(Expense).where(Expense.user_id == user_id).order_by(Expense.expense_date.desc()).limit(limit).offset(offset)
        )
        return list(result.scalars().all())

    async def get_by_date_range(self, user_id: str, start: date, end: date) -> list[Expense]:
        result = await self.db.execute(
            select(Expense).where(
                Expense.user_id == user_id,
                Expense.expense_date >= start,
                Expense.expense_date <= end,
            ).order_by(Expense.expense_date.desc())
        )
        return list(result.scalars().all())

    async def get_total_by_user_month(self, user_id: str, year: int, month: int) -> Decimal:
        result = await self.db.execute(
            select(func.coalesce(func.sum(Expense.amount), 0)).where(
                Expense.user_id == user_id,
                func.strftime("%Y", Expense.expense_date) == str(year),
                func.strftime("%m", Expense.expense_date) == f"{month:02d}",
            )
        )
        return result.scalar() or Decimal("0")

    async def create(self, user_id: str, **kwargs) -> Expense:
        expense = Expense(user_id=user_id, **kwargs)
        self.db.add(expense)
        await self.db.flush()
        await self.db.refresh(expense)
        return expense

    async def delete(self, expense: Expense) -> None:
        await self.db.delete(expense)
        await self.db.flush()
