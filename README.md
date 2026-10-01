# Tutor Tracker

REST API для репетитора: ведёт учеников, занятия и считает прогресс
(количество уроков, часы, долю выполненных домашних заданий).

**Стек:** Python 3.12, FastAPI, SQLAlchemy 2.0, SQLite, Pydantic v2, pytest, Docker.

## Запуск

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Документация API (Swagger) откроется на http://127.0.0.1:8000/docs

## Через Docker

```bash
docker build -t tutor-tracker .
docker run -p 8000:8000 tutor-tracker
```

## Тесты

```bash
pytest
```

## Эндпоинты

| Метод  | URL                         | Что делает                    |
|--------|-----------------------------|-------------------------------|
| POST   | /students                   | добавить ученика              |
| GET    | /students                   | список учеников               |
| GET    | /students/{id}              | один ученик                   |
| DELETE | /students/{id}              | удалить ученика и его уроки   |
| POST   | /students/{id}/lessons      | добавить занятие              |
| GET    | /students/{id}/lessons      | занятия ученика               |
| GET    | /students/{id}/stats        | статистика прогресса          |

## Идеи для развития

- авторизация (JWT), чтобы у каждого репетитора были свои ученики
- PostgreSQL + Alembic для миграций
- Telegram-бот поверх этого API
- веб-интерфейс на React или HTMX

## Автор и лицензия

Автор: [Hadwoker](https://github.com/Hadwoker). Лицензия: MIT (см. файл `LICENSE`).
