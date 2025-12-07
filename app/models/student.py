"""
Student model - represents a student in the system.
"""

import uuid
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base


class Student(Base):
    """
    Student database model.
    
    Attributes:
        id: Unique identifier (UUID)
        student_number: Unique student number (used for login)
        password_hash: Bcrypt hashed password
        name: Student's full name
        created_at: Timestamp when record was created
        updated_at: Timestamp when record was last updated
    """
    
    __tablename__ = "students"
    
    # Primary key - UUID for better security and distributed system support
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # Unique student number - used for authentication
    student_number = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )
    
    # Bcrypt hashed password - never store plain text passwords
    password_hash = Column(String(255), nullable=False)
    
    # Student's full name
    name = Column(String(255), nullable=False)
    
    # Timestamps - automatically managed
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
    
    def __repr__(self):
        return f"<Student(id={self.id}, student_number={self.student_number}, name={self.name})>"

