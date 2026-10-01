import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


@pytest.fixture
def client():
    # отдельная БД в памяти для каждого теста
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine, autoflush=False)

    def override_get_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def make_student(client, name="Аня"):
    return client.post("/students", json={"name": name}).json()


def test_create_and_get_student(client):
    created = make_student(client)
    assert created["name"] == "Аня"
    assert client.get(f"/students/{created['id']}").status_code == 200


def test_student_not_found(client):
    assert client.get("/students/999").status_code == 404


def test_empty_name_is_rejected(client):
    assert client.post("/students", json={"name": ""}).status_code == 422


def test_stats(client):
    sid = make_student(client)["id"]
    lessons = [
        {"lesson_date": "2026-10-01", "topic": "Переменные", "duration_min": 60, "homework_done": True},
        {"lesson_date": "2026-10-08", "topic": "Циклы", "duration_min": 90, "homework_done": False},
    ]
    for lesson in lessons:
        assert client.post(f"/students/{sid}/lessons", json=lesson).status_code == 201

    stats = client.get(f"/students/{sid}/stats").json()
    assert stats["lessons_count"] == 2
    assert stats["total_hours"] == 2.5
    assert stats["homework_rate"] == 0.5
    assert stats["last_lesson"] == "2026-10-08"
    assert stats["topics"] == ["Переменные", "Циклы"]


def test_stats_for_student_without_lessons(client):
    sid = make_student(client)["id"]
    stats = client.get(f"/students/{sid}/stats").json()
    assert stats["lessons_count"] == 0
    assert stats["last_lesson"] is None


def test_delete_student_removes_lessons(client):
    sid = make_student(client)["id"]
    client.post(
        f"/students/{sid}/lessons",
        json={"lesson_date": "2026-10-01", "topic": "Intro", "duration_min": 60},
    )
    assert client.delete(f"/students/{sid}").status_code == 204
    assert client.get(f"/students/{sid}/lessons").status_code == 404
