"""
Pydantic schemas for course registrations (read-only for Phase 3).
"""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class RegistrationBase(BaseModel):
    id: UUID = Field(..., description="Registration ID")
    course_id: UUID = Field(..., description="Course ID")
    student_id: UUID = Field(..., description="Student ID")
    status: str = Field(..., description="ENROLLED or RESERVED")
    reserve_position: int | None = Field(None, description="Queue position if RESERVED")
    created_at: datetime = Field(..., description="Created timestamp")
    updated_at: datetime = Field(..., description="Last updated timestamp")

    class Config:
        from_attributes = True


class MyCourse(BaseModel):
    """
    Combined view of the student's course and registration status.
    """
    course_id: UUID
    course_name: str
    professor: str
    schedule: str
    status: str
    reserve_position: int | None = None

    class Config:
        from_attributes = True

