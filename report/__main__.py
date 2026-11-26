from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

from report.load import load_dataset
from report.report import build_report, render_text, write_csv


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Отчёт: выплачено / осталось по работам и договорам на дату."
    )
    parser.add_argument(
        "--date",
        required=True,
        help="Дата отчёта YYYY-MM-DD (включительно).",
    )
    parser.add_argument(
        "--data",
        default="data",
        help="Папка с contracts.csv, works.csv, payments.csv (по умолчанию: data).",
    )
    parser.add_argument(
        "--csv",
        dest="csv_dir",
        default=None,
        help="Если указано — записать CSV-отчёты в эту папку.",
    )
    args = parser.parse_args(argv)

    as_of = datetime.strptime(args.date, "%Y-%m-%d").date()
    data_dir = Path(args.data)
    if not data_dir.is_dir():
        print(f"Нет папки данных: {data_dir}", file=sys.stderr)
        return 1

    dataset = load_dataset(data_dir)
    report = build_report(dataset, as_of)
    print(render_text(report))

    if args.csv_dir:
        out = Path(args.csv_dir)
        write_csv(report, out)
        print(f"CSV записаны в {out.resolve()}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
