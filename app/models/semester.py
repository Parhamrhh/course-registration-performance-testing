"""
Semester model - represents an academic semester with registration windows.
"""

import uuid
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base


class Semester(Base):
    """
    Semester database model.
    
    Attributes:
        id: Unique identifier (UUID)
        name: Semester name (e.g., "Fall 2024", "Spring 2025")
        registration_start: When registration opens (timestamp)
        registration_end: When registration closes (timestamp)
        created_at: Timestamp when record was created
        updated_at: Timestamp when record was last updated
    """
    
    __tablename__ = "semesters"
    
    # Primary key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # Semester name (e.g., "Fall 2024")
    name = Column(String(100), nullable=False)
    
    # Registration window - students can only register during this period
    registration_start = Column(DateTime(timezone=True), nullable=False)
    registration_end = Column(DateTime(timezone=True), nullable=False)
    
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
    
    def __repr__(self):
        return f"<Semester(id={self.id}, name={self.name})>"

