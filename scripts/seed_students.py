"""
Seed 1,000 test students into the database.
Each student has format STU + 5-digit number (e.g., STU40015, STU99999).
All students have password: test123

Usage (from repo root):
    docker-compose exec api python scripts/seed_students.py
"""

import sys
import uuid
import random
from pathlib import Path
from sqlalchemy.orm import Session

# Ensure the application package is importable when run as a script
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from app.database import SessionLocal
from app.auth.utils import get_password_hash
from app.models.student import Student


def seed_students(count: int = 1000) -> None:
    """
    Seed multiple test students with unique 5-digit numbers.
    
    Uses a predictable range (10000-10999) to ensure Locust can reliably
    generate matching student numbers. If more than 10,000 students are needed,
    the range can be extended.
    
    Args:
        count: Number of students to create (default: 1000)
    """
    db: Session = SessionLocal()
    try:
        # Use a predictable range for easier Locust testing
        # Range: 10000 to 10999 (ensures 1,000 students can be created)
        # This allows Locust to generate student numbers in the same range
        if count > 10000:
            raise ValueError(f"Cannot create more than 10,000 students with current range. Requested: {count}")
        
        all_numbers = list(range(10000, 10000 + count))
        random.shuffle(all_numbers)  # Shuffle for randomness, but use predictable range
        
        # Take first 'count' numbers
        selected_numbers = all_numbers[:count]
        
        password_hash = get_password_hash("test123")
        created_count = 0
        updated_count = 0
        
        for num in selected_numbers:
            student_number = f"STU{num:05d}"  # Format as STU40015, etc.
            name = f"Test Student {student_number}"
            
            # Check if student already exists
            existing = (
                db.query(Student)
                .filter(Student.student_number == student_number)
                .first()
            )
            
            if existing:
                # Update existing student
                existing.password_hash = password_hash
                existing.name = name
                db.add(existing)
                updated_count += 1
            else:
                # Create new student
                student = Student(
                    id=uuid.uuid4(),
                    student_number=student_number,
                    password_hash=password_hash,
                    name=name,
                )
                db.add(student)
                created_count += 1
        
        db.commit()
        print(f"Seeded {count} students:")
        print(f"  - Created: {created_count}")
        print(f"  - Updated: {updated_count}")
        min_num = min(selected_numbers)
        max_num = max(selected_numbers)
        print(f"  - Format: STU{min_num:05d} to STU{max_num:05d}")
        print(f"  - Password: test123")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding students: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_students(1000)

