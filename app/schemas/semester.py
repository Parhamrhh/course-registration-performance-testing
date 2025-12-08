"""
Pydantic schemas for semesters.
"""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class SemesterBase(BaseModel):
    id: UUID = Field(..., description="Semester ID")
    name: str = Field(..., description="Semester name")
    registration_start: datetime = Field(..., description="Registration start time (UTC)")
    registration_end: datetime = Field(..., description="Registration end time (UTC)")
    created_at: datetime = Field(..., description="Created timestamp")
    updated_at: datetime = Field(..., description="Last updated timestamp")

    class Config:
        from_attributes = True


class SemesterDetail(SemesterBase):
    """
    Detailed semester info.
    """
    pass

