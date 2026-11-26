from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from pathlib import Path

from report.allocate import allocate
from report.load import Dataset
from report.money import format_money, money


@dataclass(frozen=True)
class WorkRow:
    contract_id: str
    contractor: str
    work_id: str
    title: str
    status: str
    price: Decimal
    paid: Decimal
    remaining: Decimal
    linked_paid: Decimal
    from_pool: Decimal


@dataclass(frozen=True)
class ContractRow:
    contract_id: str
    contractor: str
    contract_amount: Decimal
    active_works_price: Decimal
    paid: Decimal
    remaining_on_works: Decimal
    unallocated_pool: Decimal
    queued: Decimal


@dataclass(frozen=True)
class Report:
    as_of: date
    work_rows: list[WorkRow]
    contract_rows: list[ContractRow]


def build_report(dataset: Dataset, as_of: date) -> Report:
    allocations = allocate(dataset, as_of)

    work_rows: list[WorkRow] = []
    contract_rows: list[ContractRow] = []

    for contract in dataset.contracts:
        alloc = allocations[contract.contract_id]
        active_price = sum(
            (w.price for w in alloc.works if w.status_on_date != "cancelled"),
            money(0),
        )
        for w in alloc.works:
            work_rows.append(
                WorkRow(
                    contract_id=contract.contract_id,
                    contractor=contract.contractor,
                    work_id=w.work.work_id,
                    title=w.work.title,
                    status=w.status_on_date,
                    price=w.price,
                    paid=w.paid,
                    remaining=w.remaining,
                    linked_paid=w.linked_paid,
                    from_pool=w.allocated_from_pool,
                )
            )
        contract_rows.append(
            ContractRow(
                contract_id=contract.contract_id,
                contractor=contract.contractor,
                contract_amount=contract.amount,
                active_works_price=active_price,
                paid=alloc.paid_total,
                remaining_on_works=alloc.remaining_total,
                unallocated_pool=alloc.unallocated_pool,
                queued=alloc.queued_total,
            )
        )

    return Report(as_of=as_of, work_rows=work_rows, contract_rows=contract_rows)


def render_text(report: Report) -> str:
    lines: list[str] = []
    lines.append(f"Отчёт на дату: {report.as_of.isoformat()}")
    lines.append("")
    lines.append("=== Работы ===")
    lines.append(
        f"{'contract':8} {'work':6} {'status':10} {'price':>12} {'paid':>12} "
        f"{'remain':>12} {'linked':>12} {'pool':>12}  title"
    )
    for r in report.work_rows:
        lines.append(
            f"{r.contract_id:8} {r.work_id:6} {r.status:10} "
            f"{format_money(r.price):>12} {format_money(r.paid):>12} "
            f"{format_money(r.remaining):>12} {format_money(r.linked_paid):>12} "
            f"{format_money(r.from_pool):>12}  {r.title}"
        )

    lines.append("")
    lines.append("=== Договоры ===")
    lines.append(
        f"{'contract':8} {'amount':>12} {'works_price':>12} {'paid':>12} "
        f"{'remain':>12} {'unalloc':>12} {'queued':>12}  contractor"
    )
    for r in report.contract_rows:
        lines.append(
            f"{r.contract_id:8} {format_money(r.contract_amount):>12} "
            f"{format_money(r.active_works_price):>12} {format_money(r.paid):>12} "
            f"{format_money(r.remaining_on_works):>12} "
            f"{format_money(r.unallocated_pool):>12} {format_money(r.queued):>12}  "
            f"{r.contractor}"
        )
    lines.append("")
    return "\n".join(lines)


def write_csv(report: Report, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    works_path = out_dir / "works_report.csv"
    contracts_path = out_dir / "contracts_report.csv"

    with works_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "contract_id",
                "contractor",
                "work_id",
                "title",
                "status",
                "price",
                "paid",
                "remaining",
                "linked_paid",
                "from_pool",
            ],
        )
        writer.writeheader()
        for r in report.work_rows:
            writer.writerow(
                {
                    "contract_id": r.contract_id,
                    "contractor": r.contractor,
                    "work_id": r.work_id,
                    "title": r.title,
                    "status": r.status,
                    "price": format_money(r.price),
                    "paid": format_money(r.paid),
                    "remaining": format_money(r.remaining),
                    "linked_paid": format_money(r.linked_paid),
                    "from_pool": format_money(r.from_pool),
                }
            )

    with contracts_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "contract_id",
                "contractor",
                "contract_amount",
                "active_works_price",
                "paid",
                "remaining_on_works",
                "unallocated_pool",
                "queued",
            ],
        )
        writer.writeheader()
        for r in report.contract_rows:
            writer.writerow(
                {
                    "contract_id": r.contract_id,
                    "contractor": r.contractor,
                    "contract_amount": format_money(r.contract_amount),
                    "active_works_price": format_money(r.active_works_price),
                    "paid": format_money(r.paid),
                    "remaining_on_works": format_money(r.remaining_on_works),
                    "unallocated_pool": format_money(r.unallocated_pool),
                    "queued": format_money(r.queued),
                }
            )
