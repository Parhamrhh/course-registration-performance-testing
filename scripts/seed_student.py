"""
Seed a test student into the database with a known password.

Usage (from repo root):
    docker-compose exec api python scripts/seed_student.py

Environment:
    Uses DATABASE_URL from the running container (already set in docker-compose).
"""

import uuid
import sys
from pathlib import Path
from sqlalchemy.orm import Session

# Ensure the application package is importable when run as a script
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from app.database import SessionLocal
from app.auth.utils import get_password_hash
from app.models.student import Student


def seed_student(
    student_number: str = "STU001",
    password: str = "test123",
    name: str = "Test Student",
) -> None:
    """
    Create or update a student with the given credentials.
    If the student exists, the password is updated.
    """
    db: Session = SessionLocal()
    try:
        student = (
            db.query(Student)
            .filter(Student.student_number == student_number)
            .first()
        )

        hashed = get_password_hash(password)

        if student:
            student.password_hash = hashed
            student.name = name
            db.add(student)
            action = "updated"
        else:
            student = Student(
                id=uuid.uuid4(),
                student_number=student_number,
                password_hash=hashed,
                name=name,
            )
            db.add(student)
            action = "created"

        db.commit()
        print(f"Student {action}: {student_number} (password: {password})")
    finally:
        db.close()


if __name__ == "__main__":
    seed_student()

