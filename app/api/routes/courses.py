"""
Course read-only endpoints.
"""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.course import Course
from app.models.semester import Semester
from app.schemas.course import CourseBase, CourseDetail


router = APIRouter(
    tags=["courses"],
)


@router.get("/semesters/{semester_id}/courses", response_model=list[CourseBase])
def list_courses_for_semester(semester_id: UUID, db: Session = Depends(get_db)):
    """
    List courses for a given semester.
    """
    # Ensure semester exists
    semester_exists = db.query(Semester.id).filter(Semester.id == semester_id).first()
    if not semester_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Semester not found",
        )

    courses = (
        db.query(Course)
        .filter(Course.semester_id == semester_id)
        .order_by(Course.course_name.asc())
        .all()
    )
    return courses


@router.get("/courses/{course_id}", response_model=CourseDetail)
def get_course(course_id: UUID, db: Session = Depends(get_db)):
    """
    Get course details by ID.
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )
    return course

