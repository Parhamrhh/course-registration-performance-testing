"""
Seed additional semesters into the database.
Adds 5 more semesters following the existing data structure.

Usage (from repo root):
    docker-compose exec api python scripts/seed_semesters.py
"""

import sys
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import List, Tuple
from sqlalchemy.orm import Session

# Ensure the application package is importable when run as a script
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from app.database import SessionLocal
from app.models.semester import Semester


def get_or_create_semester(
    db: Session,
    name: str,
    reg_start: datetime,
    reg_end: datetime,
) -> Semester:
    """
    Get existing semester or create new one.
    
    Args:
        db: Database session
        name: Semester name
        reg_start: Registration start time
        reg_end: Registration end time
    
    Returns:
        Semester object
    """
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


def seed_semesters() -> None:
    """
    Seed 5 additional semesters into the database.
    """
    db: Session = SessionLocal()
    try:
        # Get current time for reference
        now = datetime.now(timezone.utc)
        
        # Define 5 additional semesters
        # Mix of past, current, and future semesters
        semesters_data: List[Tuple[str, datetime, datetime]] = [
            (
                "Spring 2026",
                datetime(2026, 2, 1, 8, 0, tzinfo=timezone.utc),
                datetime(2026, 2, 3, 23, 0, tzinfo=timezone.utc),
            ),
            (
                "Fall 2026",
                datetime(2026, 9, 1, 8, 0, tzinfo=timezone.utc),
                datetime(2026, 9, 3, 23, 0, tzinfo=timezone.utc),
            ),
            (
                "Winter 2026",
                datetime(2026, 1, 5, 8, 0, tzinfo=timezone.utc),
                datetime(2026, 1, 7, 23, 0, tzinfo=timezone.utc),
            ),
            (
                "Spring 2027",
                datetime(2027, 2, 1, 8, 0, tzinfo=timezone.utc),
                datetime(2027, 2, 3, 23, 0, tzinfo=timezone.utc),
            ),
            (
                "Summer 2027",
                datetime(2027, 6, 1, 8, 0, tzinfo=timezone.utc),
                datetime(2027, 6, 3, 23, 0, tzinfo=timezone.utc),
            ),
        ]
        
        created_count = 0
        updated_count = 0
        
        for name, start, end in semesters_data:
            existing = db.query(Semester).filter(Semester.name == name).first()
            if existing:
                existing.registration_start = start
                existing.registration_end = end
                updated_count += 1
            else:
                semester = get_or_create_semester(db, name, start, end)
                created_count += 1
        
        db.commit()
        print(f"Seeded semesters:")
        print(f"  - Created: {created_count}")
        print(f"  - Updated: {updated_count}")
        print(f"  - Total semesters processed: {len(semesters_data)}")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding semesters: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_semesters()

