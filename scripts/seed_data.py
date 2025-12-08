"""
Seed baseline semesters and courses for testing read endpoints.

Usage (from repo root):
    docker-compose exec api python scripts/seed_data.py
"""

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Tuple
import uuid

from sqlalchemy.orm import Session

# Ensure the application package is importable when run as a script
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from app.database import SessionLocal
from app.models.semester import Semester
from app.models.course import Course


def get_or_create_semester(
    db: Session,
    name: str,
    reg_start: datetime,
    reg_end: datetime,
) -> Semester:
    semester = db.query(Semester).filter(Semester.name == name).first()
    if semester:
        semester.registration_start = reg_start
        semester.registration_end = reg_end
    else:
        semester = Semester(
            id=uuid.uuid4(),
            name=name,
            registration_start=reg_start,
            registration_end=reg_end,
        )
        db.add(semester)
    return semester


def seed(db: Session) -> None:
    # Semester seeds (timezone-aware UTC)
    semesters_data: List[Tuple[str, datetime, datetime]] = [
        (
            "Fall 2025",
            datetime(2025, 9, 22, 8, 0, tzinfo=timezone.utc),
            datetime(2025, 9, 24, 23, 0, tzinfo=timezone.utc),
        ),
        (
            "Winter 2025",
            datetime(2025, 1, 10, 8, 0, tzinfo=timezone.utc),
            datetime(2025, 1, 12, 23, 0, tzinfo=timezone.utc),
        ),
        (
            "Summer 2026",
            datetime(2026, 7, 1, 8, 0, tzinfo=timezone.utc),
            datetime(2026, 7, 3, 23, 0, tzinfo=timezone.utc),
        ),
    ]

    semesters = {}
    for name, start, end in semesters_data:
        semester = get_or_create_semester(db, name, start, end)
        semesters[name] = semester

    db.flush()  # Ensure semester IDs are available

    # Course seeds (name, professor, schedule, max_capacity, reserve_limit, semester_name)
    courses_data = [
        ("Computer Architecture", "James", "Sat/Mon 14:00-16:00", 45, 10, "Fall 2025"),
        ("Algorithms", "Alice", "Tue/Thu 10:00-11:30", 60, 10, "Fall 2025"),
        ("Data Structures", "Bob", "Mon/Wed 09:00-10:30", 55, 10, "Winter 2025"),
        ("Operating Systems", "Carol", "Tue/Thu 14:00-15:30", 50, 10, "Winter 2025"),
        ("Databases", "Dave", "Mon/Wed 13:00-14:30", 50, 10, "Summer 2026"),
        ("Computer Networks", "Eve", "Tue/Thu 09:00-10:30", 45, 10, "Summer 2026"),
    ]

    for name, professor, schedule, max_cap, reserve_limit, semester_name in courses_data:
        semester = semesters[semester_name]
        course = (
            db.query(Course)
            .filter(
                Course.course_name == name,
                Course.semester_id == semester.id,
            )
            .first()
        )
        if course:
            course.professor = professor
            course.schedule = schedule
            course.max_capacity = max_cap
            course.reserve_limit = reserve_limit
        else:
            course = Course(
                id=uuid.uuid4(),
                semester_id=semester.id,
                course_name=name,
                professor=professor,
                schedule=schedule,
                max_capacity=max_cap,
                reserve_limit=reserve_limit,
            )
            db.add(course)

    db.commit()
    print("Seeded semesters and courses.")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed(db)
    finally:
        db.close()

