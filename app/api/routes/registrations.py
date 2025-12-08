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
from app.schemas.registration import MyCourse, RegisterResponse, DropResponse
from app.models.course import Course
from app.models.student import Student
from app.services.registration_service import (
    register_student_for_course,
    drop_student_from_course,
    RegistrationError,
)


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


@router.post("/courses/{course_id}/register", response_model=RegisterResponse)
def register_for_course(
    course_id: UUID,
    db: Session = Depends(get_db),
    current_student: Student = Depends(get_current_student),
):
    """
    Register the authenticated student for a course.
    Respects semester registration window and capacity/reserve limits.
    """
    try:
        status_value, reserve_position = register_student_for_course(
            db, current_student.id, course_id
        )
        db.commit()
        return RegisterResponse(
            course_id=course_id,
            status=status_value,
            reserve_position=reserve_position,
        )
    except RegistrationError as exc:
        db.rollback()
        raise HTTPException(status_code=exc.status_code, detail=str(exc))
    except Exception:
        db.rollback()
        raise


@router.post("/courses/{course_id}/drop", response_model=DropResponse)
def drop_course(
    course_id: UUID,
    db: Session = Depends(get_db),
    current_student: Student = Depends(get_current_student),
):
    """
    Drop the authenticated student's registration for a course.
    If enrolled, auto-promotes the first reserved student.
    """
    try:
        (
            dropped_status,
            promoted_student_id,
            promoted_from_position,
        ) = drop_student_from_course(
            db, current_student.id, course_id
        )
        db.commit()
        return DropResponse(
            course_id=course_id,
            dropped_status=dropped_status,
            promoted_student_id=promoted_student_id,
            promoted_from_position=promoted_from_position,
        )
    except RegistrationError as exc:
        db.rollback()
        raise HTTPException(status_code=exc.status_code, detail=str(exc))
    except Exception:
        db.rollback()
        raise

