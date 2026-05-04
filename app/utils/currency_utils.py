from decimal import Decimal

SUPPORTED_CURRENCIES = ["USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF", "CNY", "INR"]


def format_currency(amount: Decimal, currency: str = "USD") -> str:
    return f"{currency} {amount:,.2f}"


def is_valid_currency(currency: str) -> bool:
    return currency.upper() in SUPPORTED_CURRENCIES
