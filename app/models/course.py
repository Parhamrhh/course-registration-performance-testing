"""
Course model - represents a course offered in a semester.
"""

import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Course(Base):
    """
    Course database model.
    
    Attributes:
        id: Unique identifier (UUID)
        semester_id: Foreign key to semesters table
        course_name: Name of the course
        professor: Professor teaching the course
        schedule: Course schedule information
        max_capacity: Maximum number of enrolled students
        reserve_limit: Maximum number of students on reserve list (default: 10)
        created_at: Timestamp when record was created
        updated_at: Timestamp when record was last updated
    """
    
    __tablename__ = "courses"
    
    # Primary key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # Foreign key to semesters table
    semester_id = Column(
        UUID(as_uuid=True),
        ForeignKey("semesters.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Course information
    course_name = Column(String(255), nullable=False)
    professor = Column(String(255), nullable=False)
    schedule = Column(String(255), nullable=False)  # e.g., "Mon/Wed 10:00-11:30"
    
    # Capacity constraints
    max_capacity = Column(Integer, nullable=False)  # Maximum enrolled students
    reserve_limit = Column(Integer, nullable=False, default=10)  # Maximum reserve list size
    
    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Relationship to semester (optional, for easier querying)
    semester = relationship("Semester", backref="courses")
    
    def __repr__(self):
        return f"<Course(id={self.id}, course_name={self.course_name}, max_capacity={self.max_capacity})>"

