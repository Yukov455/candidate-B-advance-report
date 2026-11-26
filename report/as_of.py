from __future__ import annotations

from datetime import date
from decimal import Decimal

from report.load import Payment, Work
from report.money import money


def work_status_on(work: Work, as_of: date) -> str:
    """Reconstruct work status as of a date (do not trust CSV snapshot blindly)."""
    if work.cancelled_at is not None and work.cancelled_at <= as_of:
        return "cancelled"
    if work.completed_at is not None and work.completed_at <= as_of:
        return "done"
    return "planned"


KNOWN_PAYMENT_STATUSES = frozenset({"paid", "queued", "refunded"})


def payment_counts_as_paid(payment: Payment, as_of: date) -> bool:
    """Whether the payment contributes to 'выплачено' on as_of."""
    if payment.status not in KNOWN_PAYMENT_STATUSES:
        raise ValueError(
            f"payment {payment.payment_id}: unknown status {payment.status!r}"
        )
    if payment.status == "queued":
        return False
    if payment.status == "paid":
        return payment.paid_at is not None and payment.paid_at <= as_of
    if payment.status == "refunded":
        if payment.paid_at is None or payment.paid_at > as_of:
            return False
        # Still out with contractor if refund has not happened yet as of date.
        return payment.refunded_at is None or payment.refunded_at > as_of
    return False


def obligation_price(work: Work, as_of: date) -> Decimal:
    """Price obligation for the report: zero if cancelled on/before as_of."""
    if work_status_on(work, as_of) == "cancelled":
        return money(0)
    return work.price
