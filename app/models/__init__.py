"""
Database models package.
Exports all models for easy importing.
"""

from app.models.student import Student
from app.models.semester import Semester
from app.models.course import Course
from app.models.course_registration import CourseRegistration

__all__ = ["Student", "Semester", "Course", "CourseRegistration"]

