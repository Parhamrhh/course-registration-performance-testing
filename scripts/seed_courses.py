"""
Seed additional courses into the database.
Adds 10 more courses following the existing data structure.

Usage (from repo root):
    docker-compose exec api python scripts/seed_courses.py
"""

import sys
import uuid
from pathlib import Path
from sqlalchemy.orm import Session

# Ensure the application package is importable when run as a script
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from app.database import SessionLocal
from app.models.course import Course
from app.models.semester import Semester


def seed_courses() -> None:
    """
    Seed 10 additional courses into the database.
    Courses are distributed across available semesters.
    """
    db: Session = SessionLocal()
    try:
        # Get all available semesters
        semesters = db.query(Semester).all()
        
        if not semesters:
            print("Warning: No semesters found. Please seed semesters first.")
            return
        
        # Define 10 additional courses
        # Format: (course_name, professor, schedule, max_capacity, reserve_limit)
        courses_data = [
            ("Machine Learning", "Dr. Smith", "Mon/Wed 10:00-11:30", 50, 10),
            ("Web Development", "Dr. Johnson", "Tue/Thu 14:00-15:30", 60, 10),
            ("Mobile App Development", "Dr. Williams", "Mon/Wed 13:00-14:30", 45, 10),
            ("Cloud Computing", "Dr. Brown", "Tue/Thu 09:00-10:30", 55, 10),
            ("Cybersecurity", "Dr. Davis", "Mon/Wed 15:00-16:30", 40, 10),
            ("Software Engineering", "Dr. Miller", "Tue/Thu 11:00-12:30", 50, 10),
            ("Artificial Intelligence", "Dr. Wilson", "Mon/Wed 11:00-12:30", 45, 10),
            ("Blockchain Technology", "Dr. Moore", "Tue/Thu 13:00-14:30", 35, 10),
            ("Game Development", "Dr. Taylor", "Mon/Wed 14:00-15:30", 40, 10),
            ("Data Science", "Dr. Anderson", "Tue/Thu 10:00-11:30", 55, 10),
        ]
        
        created_count = 0
        updated_count = 0
        
        # Distribute courses across semesters (round-robin)
        for idx, (course_name, professor, schedule, max_cap, reserve_limit) in enumerate(courses_data):
            # Select semester in round-robin fashion
            semester = semesters[idx % len(semesters)]
            
            # Check if course already exists
            existing = (
                db.query(Course)
                .filter(
                    Course.course_name == course_name,
                    Course.semester_id == semester.id,
                )
                .first()
            )
            
            if existing:
                # Update existing course
                existing.professor = professor
                existing.schedule = schedule
                existing.max_capacity = max_cap
                existing.reserve_limit = reserve_limit
                updated_count += 1
            else:
                # Create new course
                course = Course(
                    id=uuid.uuid4(),
                    semester_id=semester.id,
                    course_name=course_name,
                    professor=professor,
                    schedule=schedule,
                    max_capacity=max_cap,
                    reserve_limit=reserve_limit,
                )
                db.add(course)
                created_count += 1
        
        db.commit()
        print(f"Seeded courses:")
        print(f"  - Created: {created_count}")
        print(f"  - Updated: {updated_count}")
        print(f"  - Total courses processed: {len(courses_data)}")
        print(f"  - Distributed across {len(semesters)} semesters")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding courses: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_courses()

