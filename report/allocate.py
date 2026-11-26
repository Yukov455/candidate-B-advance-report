from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from report.as_of import obligation_price, payment_counts_as_paid, work_status_on
from report.load import Dataset, Payment, Work
from report.money import money


@dataclass(frozen=True)
class WorkAllocation:
    work: Work
    status_on_date: str
    price: Decimal
    linked_paid: Decimal
    allocated_from_pool: Decimal
    paid: Decimal
    remaining: Decimal


@dataclass(frozen=True)
class ContractAllocation:
    contract_id: str
    works: list[WorkAllocation]
    pool_total: Decimal
    unallocated_pool: Decimal
    paid_total: Decimal
    remaining_total: Decimal
    queued_total: Decimal


def allocate(dataset: Dataset, as_of: date) -> dict[str, ContractAllocation]:
    by_contract: dict[str, list[Work]] = {}
    for work in dataset.works:
        by_contract.setdefault(work.contract_id, []).append(work)

    result: dict[str, ContractAllocation] = {}
    contract_ids = {c.contract_id for c in dataset.contracts} | set(by_contract)
    for contract_id in sorted(contract_ids):
        works = by_contract.get(contract_id, [])
        payments = [p for p in dataset.payments if p.contract_id == contract_id]
        result[contract_id] = _allocate_contract(contract_id, works, payments, as_of)
    return result


def _allocate_contract(
    contract_id: str,
    works: list[Work],
    payments: list[Payment],
    as_of: date,
) -> ContractAllocation:
    linked: dict[str, Decimal] = {w.work_id: money(0) for w in works}
    pool = money(0)
    paid_total = money(0)
    queued_total = money(0)

    for payment in payments:
        if payment.status == "queued" and payment.created_at <= as_of:
            queued_total += payment.amount
        if not payment_counts_as_paid(payment, as_of):
            continue
        paid_total += payment.amount
        if payment.work_id:
            if payment.work_id not in linked:
                raise ValueError(
                    f"payment {payment.payment_id}: unknown work_id {payment.work_id!r} "
                    f"for contract {contract_id}"
                )
            linked[payment.work_id] += payment.amount
        else:
            pool += payment.amount

    remaining_pool = pool
    allocations: list[WorkAllocation] = []

    for work in _fifo_order(works, as_of):
        status = work_status_on(work, as_of)
        price = obligation_price(work, as_of)
        linked_paid = linked.get(work.work_id, money(0))
        allocated = money(0)
        if status != "cancelled":
            need = price - linked_paid
            if need < 0:
                need = money(0)
            allocated = min(need, remaining_pool)
            remaining_pool -= allocated
        paid = linked_paid + allocated
        remaining = price - paid
        allocations.append(
            WorkAllocation(
                work=work,
                status_on_date=status,
                price=price,
                linked_paid=linked_paid,
                allocated_from_pool=allocated,
                paid=paid,
                remaining=remaining,
            )
        )

    # Keep original CSV order in output for readability.
    order = {w.work_id: i for i, w in enumerate(works)}
    allocations.sort(key=lambda a: order.get(a.work.work_id, 10_000))

    remaining_total = sum((a.remaining for a in allocations), money(0))
    return ContractAllocation(
        contract_id=contract_id,
        works=allocations,
        pool_total=pool,
        unallocated_pool=remaining_pool,
        paid_total=paid_total,
        remaining_total=remaining_total,
        queued_total=queued_total,
    )


def _fifo_order(works: list[Work], as_of: date) -> list[Work]:
    def sort_key(work: Work):
        status = work_status_on(work, as_of)
        if status == "done":
            return (0, work.completed_at or date.max, work.work_id)
        if status == "planned":
            return (1, date.max, work.work_id)
        return (2, date.max, work.work_id)

    return sorted(works, key=sort_key)
