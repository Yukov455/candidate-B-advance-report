from datetime import date
from decimal import Decimal
from pathlib import Path

from report.allocate import allocate
from report.load import load_dataset

DATA = Path(__file__).resolve().parents[1] / "data"
AS_OF = date(2026, 11, 10)


def test_fixture_paid_totals():
    ds = load_dataset(DATA)
    result = allocate(ds, AS_OF)
    assert result["D-1"].paid_total == Decimal("315000.00")
    assert result["D-2"].paid_total == Decimal("75000.00")


def test_fixture_d1_fifo_split():
    ds = load_dataset(DATA)
    by_id = {a.work.work_id: a for a in allocate(ds, AS_OF)["D-1"].works}

    assert by_id["W-11"].paid == Decimal("100000.00")
    assert by_id["W-11"].remaining == Decimal("0.00")
    assert by_id["W-12"].paid == Decimal("100000.00")
    assert by_id["W-14"].linked_paid == Decimal("15000.00")
    assert by_id["W-14"].paid == Decimal("100000.00")
    assert by_id["W-15"].paid == Decimal("15000.00")
    assert by_id["W-15"].remaining == Decimal("85000.00")
    assert by_id["W-16"].paid == Decimal("0.00")
    assert by_id["W-16"].remaining == Decimal("100000.00")
    assert by_id["W-13"].price == Decimal("0.00")
    assert by_id["W-13"].status_on_date == "cancelled"


def test_fixture_d2_w23_still_planned():
    ds = load_dataset(DATA)
    by_id = {a.work.work_id: a for a in allocate(ds, AS_OF)["D-2"].works}

    assert by_id["W-21"].paid == Decimal("20000.00")
    assert by_id["W-22"].paid == Decimal("30000.00")
    assert by_id["W-23"].status_on_date == "planned"
    assert by_id["W-23"].paid == Decimal("25000.00")
    assert by_id["W-23"].remaining == Decimal("15000.00")


def test_paid_invariant_works_plus_unallocated_equals_contract_paid():
    ds = load_dataset(DATA)
    result = allocate(ds, AS_OF)
    for contract_id, alloc in result.items():
        works_paid = sum((w.paid for w in alloc.works), Decimal("0"))
        assert works_paid + alloc.unallocated_pool == alloc.paid_total, contract_id


def test_queued_tracked_separately_for_d1():
    ds = load_dataset(DATA)
    assert allocate(ds, AS_OF)["D-1"].queued_total == Decimal("150000.00")
    assert allocate(ds, AS_OF)["D-2"].queued_total == Decimal("0.00")
