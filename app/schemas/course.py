"""
Pydantic schemas for courses.
"""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class CourseBase(BaseModel):
    id: UUID = Field(..., description="Course ID")
    semester_id: UUID = Field(..., description="Semester ID")
    course_name: str = Field(..., description="Course name")
    professor: str = Field(..., description="Professor name")
    schedule: str = Field(..., description="Course schedule")
    max_capacity: int = Field(..., description="Maximum enrolled students")
    reserve_limit: int = Field(..., description="Reserve list limit")
    created_at: datetime = Field(..., description="Created timestamp")
    updated_at: datetime = Field(..., description="Last updated timestamp")

    class Config:
        from_attributes = True


class CourseDetail(CourseBase):
    """
    Detailed course info.
    """
    pass

