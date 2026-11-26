from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

TWOPLACES = Decimal("0.01")


def money(value: str | Decimal | int) -> Decimal:
    """Parse an amount as Decimal (never float)."""
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def quantize(amount: Decimal) -> Decimal:
    return amount.quantize(TWOPLACES, rounding=ROUND_HALF_UP)


def format_money(amount: Decimal) -> str:
    return f"{quantize(amount):.2f}"
