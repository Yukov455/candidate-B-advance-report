from datetime import date
from decimal import Decimal
from pathlib import Path

from report.load import load_dataset
from report.report import build_report

DATA = Path(__file__).resolve().parents[1] / "data"
AS_OF = date(2026, 11, 10)


def test_build_report_includes_contracts_and_works():
    report = build_report(load_dataset(DATA), AS_OF)
    assert len(report.work_rows) == 9
    assert len(report.contract_rows) == 2

    d1 = next(r for r in report.contract_rows if r.contract_id == "D-1")
    assert d1.paid == Decimal("315000.00")
    assert d1.contract_amount == Decimal("600000.00")
    assert d1.queued == Decimal("150000.00")

    d2 = next(r for r in report.contract_rows if r.contract_id == "D-2")
    assert d2.paid == Decimal("75000.00")
    assert d2.remaining_on_works == Decimal("15000.00")
