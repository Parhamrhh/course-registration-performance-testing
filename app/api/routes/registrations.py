"""
Registration read endpoints (Phase 3).
"""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth.dependencies import get_current_student
from app.models.semester import Semester
from app.models.course_registration import CourseRegistration
from app.schemas.registration import MyCourse
from app.models.course import Course
from app.models.student import Student


router = APIRouter(
    tags=["registrations"],
)


@router.get("/semesters/{semester_id}/my-courses", response_model=list[MyCourse])
def get_my_courses_for_semester(
    semester_id: UUID,
    db: Session = Depends(get_db),
    current_student: Student = Depends(get_current_student),
):
    """
    Get the authenticated student's enrolled/reserved courses for a semester.
    """
    # Ensure semester exists
    semester_exists = db.query(Semester.id).filter(Semester.id == semester_id).first()
    if not semester_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Semester not found",
        )

    registrations = (
        db.query(CourseRegistration)
        .join(Course, CourseRegistration.course_id == Course.id)
        .filter(
            Course.semester_id == semester_id,
            CourseRegistration.student_id == current_student.id,
        )
        .all()
    )

    # Build response
    result: list[MyCourse] = []
    for reg in registrations:
        course = reg.course
        result.append(
            MyCourse(
                course_id=course.id,
                course_name=course.course_name,
                professor=course.professor,
                schedule=course.schedule,
                status=reg.status,
                reserve_position=reg.reserve_position,
            )
        )
    return result

