import datetime as dt

from pydantic import BaseModel, ConfigDict, Field


class StudentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    level: str = "beginner"


class StudentOut(StudentCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class LessonCreate(BaseModel):
    lesson_date: dt.date
    topic: str = Field(min_length=1, max_length=200)
    duration_min: int = Field(gt=0, le=480)
    homework_done: bool = False
    notes: str = ""


class LessonOut(LessonCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    student_id: int


class StudentStats(BaseModel):
    student_id: int
    lessons_count: int
    total_hours: float
    homework_rate: float  # доля выполненных ДЗ, от 0 до 1
    last_lesson: dt.date | None
    topics: list[str]
