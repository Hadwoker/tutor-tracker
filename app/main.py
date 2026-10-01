from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models, schemas
from .database import Base, engine, get_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)  # создаём таблицы при старте
    yield


app = FastAPI(
    title="Tutor Tracker",
    version="1.0.0",
    description="API для учёта учеников и занятий репетитора.",
    contact={"name": "Hadwoker", "url": "https://github.com/Hadwoker"},
    license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
    lifespan=lifespan,
)


def get_student_or_404(student_id: int, db: Session) -> models.Student:
    student = db.get(models.Student, student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@app.post("/students", response_model=schemas.StudentOut, status_code=201)
def create_student(data: schemas.StudentCreate, db: Session = Depends(get_db)):
    student = models.Student(**data.model_dump())
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


@app.get("/students", response_model=list[schemas.StudentOut])
def list_students(db: Session = Depends(get_db)):
    return db.scalars(select(models.Student).order_by(models.Student.name)).all()


@app.get("/students/{student_id}", response_model=schemas.StudentOut)
def read_student(student_id: int, db: Session = Depends(get_db)):
    return get_student_or_404(student_id, db)


@app.delete("/students/{student_id}", status_code=204)
def delete_student(student_id: int, db: Session = Depends(get_db)):
    student = get_student_or_404(student_id, db)
    db.delete(student)
    db.commit()


@app.post(
    "/students/{student_id}/lessons",
    response_model=schemas.LessonOut,
    status_code=201,
)
def add_lesson(
    student_id: int, data: schemas.LessonCreate, db: Session = Depends(get_db)
):
    get_student_or_404(student_id, db)
    lesson = models.Lesson(student_id=student_id, **data.model_dump())
    db.add(lesson)
    db.commit()
    db.refresh(lesson)
    return lesson


@app.get("/students/{student_id}/lessons", response_model=list[schemas.LessonOut])
def list_lessons(student_id: int, db: Session = Depends(get_db)):
    get_student_or_404(student_id, db)
    query = (
        select(models.Lesson)
        .where(models.Lesson.student_id == student_id)
        .order_by(models.Lesson.lesson_date)
    )
    return db.scalars(query).all()


@app.get("/students/{student_id}/stats", response_model=schemas.StudentStats)
def student_stats(student_id: int, db: Session = Depends(get_db)):
    student = get_student_or_404(student_id, db)
    lessons = sorted(student.lessons, key=lambda lesson: lesson.lesson_date)
    count = len(lessons)
    total_minutes = sum(lesson.duration_min for lesson in lessons)
    done = sum(1 for lesson in lessons if lesson.homework_done)

    return schemas.StudentStats(
        student_id=student.id,
        lessons_count=count,
        total_hours=round(total_minutes / 60, 2),
        homework_rate=round(done / count, 2) if count else 0.0,
        last_lesson=lessons[-1].lesson_date if lessons else None,
        topics=[lesson.topic for lesson in lessons],
    )
