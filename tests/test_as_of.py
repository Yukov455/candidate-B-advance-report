from datetime import date
from decimal import Decimal

from report.as_of import obligation_price, payment_counts_as_paid, work_status_on
from report.load import Payment, Work

AS_OF = date(2026, 11, 10)


def _work(**kwargs) -> Work:
    base = dict(
        work_id="W-x",
        contract_id="D-1",
        title="t",
        price=Decimal("100000.00"),
        status="planned",
        completed_at=None,
        cancelled_at=None,
    )
    base.update(kwargs)
    return Work(**base)


def _payment(**kwargs) -> Payment:
    base = dict(
        payment_id="P-x",
        contract_id="D-1",
        work_id=None,
        purpose="x",
        amount=Decimal("1000.00"),
        status="paid",
        created_at=date(2026, 1, 1),
        paid_at=date(2026, 1, 2),
        refunded_at=None,
    )
    base.update(kwargs)
    return Payment(**base)


def test_work_done_on_or_before_as_of():
    w = _work(status="done", completed_at=date(2026, 10, 28))
    assert work_status_on(w, AS_OF) == "done"


def test_work_completed_after_as_of_is_planned():
    w = _work(status="done", completed_at=date(2026, 11, 11))
    assert work_status_on(w, AS_OF) == "planned"


def test_work_cancelled_on_or_before_as_of():
    w = _work(status="cancelled", cancelled_at=date(2026, 10, 12))
    assert work_status_on(w, AS_OF) == "cancelled"


def test_cancelled_obligation_is_zero():
    w = _work(status="cancelled", cancelled_at=date(2026, 10, 12), price=Decimal("100000"))
    assert obligation_price(w, AS_OF) == Decimal("0")


def test_paid_counts_when_paid_at_on_or_before():
    p = _payment(status="paid", paid_at=date(2026, 11, 10))
    assert payment_counts_as_paid(p, AS_OF) is True


def test_paid_after_as_of_excluded():
    p = _payment(status="paid", paid_at=date(2026, 11, 12))
    assert payment_counts_as_paid(p, AS_OF) is False


def test_queued_never_counts():
    p = _payment(status="queued", paid_at=None)
    assert payment_counts_as_paid(p, AS_OF) is False


def test_refunded_excluded_after_refund():
    p = _payment(
        status="refunded",
        paid_at=date(2026, 9, 2),
        refunded_at=date(2026, 9, 10),
    )
    assert payment_counts_as_paid(p, AS_OF) is False


def test_refunded_counts_while_money_still_out():
    p = _payment(
        status="refunded",
        paid_at=date(2026, 9, 2),
        refunded_at=date(2026, 11, 20),
    )
    assert payment_counts_as_paid(p, AS_OF) is True
