from datetime import date, timedelta
from typing import Tuple


def get_month_range(year: int, month: int) -> Tuple[date, date]:
    start = date(year, month, 1)
    if month == 12:
        end = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end = date(year, month + 1, 1) - timedelta(days=1)
    return start, end


def get_current_month_range() -> Tuple[date, date]:
    today = date.today()
    return get_month_range(today.year, today.month)


def days_remaining_in_month() -> int:
    today = date.today()
    _, end = get_current_month_range()
    return (end - today).days
