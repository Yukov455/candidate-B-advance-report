# Как запустить

Нужен Python 3.9+ (стандартная библиотека). Для тестов — `pytest`.

```bash
cd candidate-B
python3 -m report --date 2026-11-10 --data data
```

Опционально записать CSV:

```bash
python3 -m report --date 2026-11-10 --data data --csv out
```

Тесты:

```bash
python3 -m pytest -q
```

Контрольная дата из задания: `2026-11-10`. Допущения — в `DECISIONS.md`, записка — в `NOTE_TO_ACCOUNTANT.md`.
