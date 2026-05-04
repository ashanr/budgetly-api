from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from decimal import Decimal


class ExpenseCreate(BaseModel):
    category_id: Optional[str] = None
    amount: Decimal = Field(gt=0)
    currency: str = "USD"
    description: Optional[str] = None
    merchant: Optional[str] = None
    expense_date: date
    is_recurring: bool = False
    tags: Optional[str] = None


class ExpenseUpdate(BaseModel):
    category_id: Optional[str] = None
    amount: Optional[Decimal] = Field(default=None, gt=0)
    currency: Optional[str] = None
    description: Optional[str] = None
    merchant: Optional[str] = None
    expense_date: Optional[date] = None
    is_recurring: Optional[bool] = None
    tags: Optional[str] = None


class ExpenseResponse(BaseModel):
    id: str
    user_id: str
    category_id: Optional[str] = None
    amount: Decimal
    currency: str
    description: Optional[str] = None
    merchant: Optional[str] = None
    expense_date: date
    is_recurring: bool
    tags: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
