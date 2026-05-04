from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from decimal import Decimal


class BudgetCreate(BaseModel):
    category_id: Optional[str] = None
    name: str = Field(min_length=1, max_length=200)
    amount: Decimal = Field(gt=0)
    currency: str = "USD"
    period: str = "monthly"
    start_date: date
    end_date: Optional[date] = None
    alert_threshold: int = Field(default=80, ge=0, le=100)
    notes: Optional[str] = None


class BudgetResponse(BaseModel):
    id: str
    user_id: str
    category_id: Optional[str] = None
    name: str
    amount: Decimal
    currency: str
    period: str
    start_date: date
    end_date: Optional[date] = None
    alert_threshold: int
    notes: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class BudgetHealth(BaseModel):
    budget_id: str
    name: str
    allocated: Decimal
    spent: Decimal
    remaining: Decimal
    utilization_percent: float
    health_score: float
    status: str
    is_over_budget: bool
