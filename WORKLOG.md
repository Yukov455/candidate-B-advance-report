# WORKLOG (Cursor)

Работа велась в **Cursor**, не в Claude Code. Этот файл — аналог требуемого транскрипта `/export`.

## Хронология

### 1. Изучение задания
- Прочитаны `README.md`, `data/FORMAT.md`, CSV: 2 договора, 9 работ, 8 платежей.
- Кода в папке не было — только условие и выгрузки.
- Контрольная дата: 2026-11-10.

### 2. Допущения
- Зафиксированы в `DECISIONS.md`: дата включительно; paid/queued/refunded; реконструкция статуса работы; цена cancelled = 0; FIFO-разнесение пула без `work_id`; Decimal; stdout + опциональный CSV.

### 3. Ожидаемые цифры на 10.11.2026 (проверка до кода)
- Выплачено: D-1 = 315000 (P-1+P-3); D-2 = 75000 (P-5+P-6+P-7). Исключены P-2 (refunded), P-4 (queued), P-8 (после даты).
- W-23 на дату = planned.
- FIFO: W-11/12/14 закрыты; W-15 = 15000; W-16 = 0; W-21/22 закрыты; W-23 = 25000/40000.

### 4. Реализация (TDD)
- Тесты: `tests/test_as_of.py`, `tests/test_allocate.py`, `tests/test_report_fixture.py`.
- Пакет: `report/` — `load`, `money`, `as_of`, `allocate`, `report`, `__main__`.
- Команды:
  ```bash
  python3 -m pytest -q
  # 15 passed
  python3 -m report --date 2026-11-10 --data data
  ```
- Результат CLI совпал с ожидаемыми цифрами.

### 5. Документы сдачи
- `DECISIONS.md`
- `NOTE_TO_ACCOUNTANT.md`
- `README_RUN.md`
- этот `WORKLOG.md`

### 6. Review
- Проверка python-reviewer: 3 HIGH (orphan work_id, unknown status, nullable created_at).
- Исправлено: `ValueError` на битых ссылках/статусах; обязательные даты валидируются в `load.py`.
- Повторный прогон: 15 passed, цифры на 2026-11-10 без изменений.

## Диалог (сжатый слепок сессии Cursor)

1. Пользователь: изучить `/Users/yakovpravilin/Downloads/candidate-B` и описать содержимое.
2. Ассистент: тестовое задание «аванс по договору», структура data/, суть отчёта.
3. Пользователь: изучить полностью, составить план действий.
4. Ассистент: план Python CLI + FIFO + Decimal + deliverables.
5. Пользователь: придумать, как закрыть транскрипт Claude Code `/export`.
6. Ассистент: сначала — реальный Claude Code; затем по запросу пользователя — сдача **Cursor-WORKLOG**.
7. Пользователь: выполнить план.
8. Ассистент: реализация, тесты 15 passed, документы, сверка на 2026-11-10.
