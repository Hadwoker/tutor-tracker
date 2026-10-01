import datetime as dt

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    level: Mapped[str] = mapped_column(String(50), default="beginner")

    lessons: Mapped[list["Lesson"]] = relationship(
        back_populates="student", cascade="all, delete-orphan"
    )


class Lesson(Base):
    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"))
    lesson_date: Mapped[dt.date]
    topic: Mapped[str] = mapped_column(String(200))
    duration_min: Mapped[int]
    homework_done: Mapped[bool] = mapped_column(default=False)
    notes: Mapped[str] = mapped_column(default="")

    student: Mapped[Student] = relationship(back_populates="lessons")
