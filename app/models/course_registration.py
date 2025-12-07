"""
Course Registration model - represents a student's registration for a course.
Handles both ENROLLED and RESERVED statuses with reserve queue positions.
"""

import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, UniqueConstraint, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class CourseRegistration(Base):
    """
    Course Registration database model.
    
    Represents a student's registration for a course. Can be either:
    - ENROLLED: Student is enrolled in the course (counts toward max_capacity)
    - RESERVED: Student is on the reserve/waiting list (counts toward reserve_limit)
    
    Attributes:
        id: Unique identifier (UUID)
        student_id: Foreign key to students table
        course_id: Foreign key to courses table
        status: Either "ENROLLED" or "RESERVED"
        reserve_position: Position in reserve queue (NULL if ENROLLED, 1-based if RESERVED)
        created_at: Timestamp when record was created
        updated_at: Timestamp when record was last updated
    
    Constraints:
        - UNIQUE(student_id, course_id): A student can only register once per course
        - reserve_position is NULL when status is ENROLLED
        - reserve_position is NOT NULL when status is RESERVED
    """
    
    __tablename__ = "course_registrations"
    
    # Primary key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # Foreign keys
    student_id = Column(
        UUID(as_uuid=True),
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    course_id = Column(
        UUID(as_uuid=True),
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Status: ENROLLED or RESERVED
    status = Column(
        String(20),
        nullable=False,
        index=True
    )
    
    # Reserve queue position (1-based, NULL if ENROLLED)
    # Position 1 is the next to be promoted when a spot opens
    reserve_position = Column(Integer, nullable=True, index=True)
    
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
    
    # Relationships for easier querying
    student = relationship("Student", backref="registrations")
    course = relationship("Course", backref="registrations")
    
    # Table-level constraints
    __table_args__ = (
        # Ensure a student can only register once per course
        UniqueConstraint('student_id', 'course_id', name='unique_student_course'),
        
        # Ensure reserve_position logic: NULL for ENROLLED, NOT NULL for RESERVED
        CheckConstraint(
            "(status = 'ENROLLED' AND reserve_position IS NULL) OR "
            "(status = 'RESERVED' AND reserve_position IS NOT NULL)",
            name='check_reserve_position_logic'
        ),
    )
    
    def __repr__(self):
        return f"<CourseRegistration(id={self.id}, student_id={self.student_id}, course_id={self.course_id}, status={self.status}, reserve_position={self.reserve_position})>"

