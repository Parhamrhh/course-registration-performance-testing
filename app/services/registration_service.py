"""
Registration business logic with database-level locking.
"""

from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, update

from app.models.course import Course
from app.models.semester import Semester
from app.models.course_registration import CourseRegistration


class RegistrationError(Exception):
    """Base exception for registration errors."""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.status_code = status_code


def _assert_within_window(semester: Semester, now: datetime) -> None:
    if not (semester.registration_start <= now <= semester.registration_end):
        raise RegistrationError(
            "Registration window is closed for this semester.",
            status_code=400,
        )


def register_student_for_course(
    db: Session, student_id, course_id, now: Optional[datetime] = None
) -> tuple[str, Optional[int]]:
    """
    Register a student for a course with concurrency-safe locking.

    Returns (status, reserve_position). status is "ENROLLED" or "RESERVED".
    """
    now = now or datetime.now(timezone.utc)

    # Lock the course row (and semester via join) to prevent race conditions
    course: Course = (
        db.query(Course)
        .join(Semester, Course.semester_id == Semester.id)
        .with_for_update()
        .filter(Course.id == course_id)
        .first()
    )
    if not course:
        raise RegistrationError("Course not found.", status_code=404)

    _assert_within_window(course.semester, now)

    # Check existing registration (lock relevant rows)
    existing = (
        db.query(CourseRegistration)
        .with_for_update()
        .filter(
            CourseRegistration.course_id == course_id,
            CourseRegistration.student_id == student_id,
        )
        .first()
    )
    if existing:
        raise RegistrationError("Already registered for this course.", status_code=409)

    # Lock all registrations for this course to compute counts safely
    enrolled_regs = (
        db.query(CourseRegistration)
        .with_for_update()
        .filter(
            CourseRegistration.course_id == course_id,
            CourseRegistration.status == "ENROLLED",
        )
        .all()
    )
    enrolled_count = len(enrolled_regs)

    reserved_regs = (
        db.query(CourseRegistration)
        .with_for_update()
        .filter(
            CourseRegistration.course_id == course_id,
            CourseRegistration.status == "RESERVED",
        )
        .all()
    )
    reserved_count = len(reserved_regs)

    if enrolled_count < course.max_capacity:
        reg = CourseRegistration(
            student_id=student_id,
            course_id=course_id,
            status="ENROLLED",
            reserve_position=None,
        )
        db.add(reg)
        return "ENROLLED", None

    if reserved_count < course.reserve_limit:
        # Determine next reserve position
        max_pos = (
            db.query(func.max(CourseRegistration.reserve_position))
            .filter(
                CourseRegistration.course_id == course_id,
                CourseRegistration.status == "RESERVED",
            )
            .scalar()
        )
        next_pos = (max_pos or 0) + 1
        reg = CourseRegistration(
            student_id=student_id,
            course_id=course_id,
            status="RESERVED",
            reserve_position=next_pos,
        )
        db.add(reg)
        return "RESERVED", next_pos

    raise RegistrationError("Course is full; reserve list is full.", status_code=409)


def drop_student_from_course(
    db: Session, student_id, course_id, now: Optional[datetime] = None
) -> tuple[str, Optional[str], Optional[int]]:
    """
    Drop a student's registration with auto-promotion.

    Returns (dropped_status, promoted_student_id, promoted_reserve_position_before).
    dropped_status is the status the student had before dropping.
    """
    now = now or datetime.now(timezone.utc)

    # Lock course and semester
    course: Course = (
        db.query(Course)
        .join(Semester, Course.semester_id == Semester.id)
        .with_for_update()
        .filter(Course.id == course_id)
        .first()
    )
    if not course:
        raise RegistrationError("Course not found.", status_code=404)

    _assert_within_window(course.semester, now)

    # Lock the student's registration
    reg = (
        db.query(CourseRegistration)
        .with_for_update()
        .filter(
            CourseRegistration.course_id == course_id,
            CourseRegistration.student_id == student_id,
        )
        .first()
    )
    if not reg:
        raise RegistrationError("Registration not found.", status_code=404)

    dropped_status = reg.status
    dropped_reserve_position = reg.reserve_position

    # Delete the registration
    db.delete(reg)

    promoted_student_id = None
    promoted_prev_position = None

    if dropped_status == "ENROLLED":
        # Promote first reserved (lowest reserve_position)
        to_promote = (
            db.query(CourseRegistration)
            .with_for_update()
            .filter(
                CourseRegistration.course_id == course_id,
                CourseRegistration.status == "RESERVED",
            )
            .order_by(CourseRegistration.reserve_position.asc())
            .first()
        )
        if to_promote:
            promoted_student_id = str(to_promote.student_id)
            promoted_prev_position = to_promote.reserve_position
            to_promote.status = "ENROLLED"
            to_promote.reserve_position = None

            # Shift remaining reserve positions down by 1
            db.execute(
                update(CourseRegistration)
                .where(
                    CourseRegistration.course_id == course_id,
                    CourseRegistration.status == "RESERVED",
                    CourseRegistration.reserve_position > promoted_prev_position,
                )
                .values(reserve_position=CourseRegistration.reserve_position - 1)
            )

    elif dropped_status == "RESERVED" and dropped_reserve_position is not None:
        # Shift positions for those behind the dropped position
        db.execute(
            update(CourseRegistration)
            .where(
                CourseRegistration.course_id == course_id,
                CourseRegistration.status == "RESERVED",
                CourseRegistration.reserve_position > dropped_reserve_position,
            )
            .values(reserve_position=CourseRegistration.reserve_position - 1)
        )

    return dropped_status, promoted_student_id, promoted_prev_position

