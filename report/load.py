from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

from report.money import money


def _parse_date(raw: str | None) -> date | None:
    if raw is None:
        return None
    text = raw.strip()
    if not text:
        return None
    return datetime.strptime(text, "%Y-%m-%d").date()


@dataclass(frozen=True)
class Contract:
    contract_id: str
    contractor: str
    amount: Decimal
    signed_at: date


@dataclass(frozen=True)
class Work:
    work_id: str
    contract_id: str
    title: str
    price: Decimal
    status: str
    completed_at: date | None
    cancelled_at: date | None


@dataclass(frozen=True)
class Payment:
    payment_id: str
    contract_id: str
    work_id: str | None
    purpose: str
    amount: Decimal
    status: str
    created_at: date
    paid_at: date | None
    refunded_at: date | None


@dataclass(frozen=True)
class Dataset:
    contracts: list[Contract]
    works: list[Work]
    payments: list[Payment]


def load_dataset(data_dir: Path) -> Dataset:
    return Dataset(
        contracts=_load_contracts(data_dir / "contracts.csv"),
        works=_load_works(data_dir / "works.csv"),
        payments=_load_payments(data_dir / "payments.csv"),
    )


def _require_date(raw: str | None, *, label: str) -> date:
    parsed = _parse_date(raw)
    if parsed is None:
        raise ValueError(f"{label}: missing required date")
    return parsed


def _load_contracts(path: Path) -> list[Contract]:
    rows: list[Contract] = []
    with path.open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            contract_id = row["contract_id"].strip()
            rows.append(
                Contract(
                    contract_id=contract_id,
                    contractor=row["contractor"].strip(),
                    amount=money(row["amount"]),
                    signed_at=_require_date(
                        row["signed_at"], label=f"contract {contract_id} signed_at"
                    ),
                )
            )
    return rows


def _load_works(path: Path) -> list[Work]:
    rows: list[Work] = []
    with path.open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            rows.append(
                Work(
                    work_id=row["work_id"].strip(),
                    contract_id=row["contract_id"].strip(),
                    title=row["title"].strip(),
                    price=money(row["price"]),
                    status=row["status"].strip(),
                    completed_at=_parse_date(row.get("completed_at")),
                    cancelled_at=_parse_date(row.get("cancelled_at")),
                )
            )
    return rows


def _load_payments(path: Path) -> list[Payment]:
    rows: list[Payment] = []
    with path.open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            work_raw = (row.get("work_id") or "").strip()
            payment_id = row["payment_id"].strip()
            rows.append(
                Payment(
                    payment_id=payment_id,
                    contract_id=row["contract_id"].strip(),
                    work_id=work_raw or None,
                    purpose=row["purpose"].strip(),
                    amount=money(row["amount"]),
                    status=row["status"].strip(),
                    created_at=_require_date(
                        row["created_at"],
                        label=f"payment {payment_id} created_at",
                    ),
                    paid_at=_parse_date(row.get("paid_at")),
                    refunded_at=_parse_date(row.get("refunded_at")),
                )
            )
    return rows
