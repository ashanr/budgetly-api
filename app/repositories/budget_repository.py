from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from datetime import date
from app.models.budget import Budget


class BudgetRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, budget_id: str) -> Optional[Budget]:
        result = await self.db.execute(select(Budget).where(Budget.id == budget_id))
        return result.scalar_one_or_none()

    async def get_by_user(self, user_id: str) -> list[Budget]:
        result = await self.db.execute(
            select(Budget).where(Budget.user_id == user_id).order_by(Budget.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_active_budgets(self, user_id: str, reference_date: date = None) -> list[Budget]:
        ref = reference_date or date.today()
        result = await self.db.execute(
            select(Budget).where(
                Budget.user_id == user_id,
                Budget.start_date <= ref,
            )
        )
        return list(result.scalars().all())

    async def create(self, user_id: str, **kwargs) -> Budget:
        budget = Budget(user_id=user_id, **kwargs)
        self.db.add(budget)
        await self.db.flush()
        await self.db.refresh(budget)
        return budget
