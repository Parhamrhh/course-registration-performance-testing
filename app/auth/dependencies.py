"""
FastAPI dependencies for authentication.
Provides dependency functions to protect routes with JWT authentication.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.student import Student
from app.auth.utils import decode_access_token
from app.auth.schemas import TokenData

# HTTPBearer is a FastAPI security scheme that extracts the Bearer token from the Authorization header
security = HTTPBearer()


def get_current_student(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Student:
    """
    FastAPI dependency to get the current authenticated student.
    
    This function:
    1. Extracts the JWT token from the Authorization header
    2. Decodes and validates the token
    3. Retrieves the student from the database
    4. Returns the student object
    
    If authentication fails at any step, raises HTTP 401 Unauthorized.
    
    Usage:
        @app.get("/protected")
        def protected_route(current_student: Student = Depends(get_current_student)):
            # current_student is the authenticated student
            return {"student_id": current_student.id}
    
    Args:
        credentials: HTTPBearer extracts the token from Authorization header
        db: Database session (injected by FastAPI)
    
    Returns:
        Student object for the authenticated user
    
    Raises:
        HTTPException: 401 if token is invalid or student not found
    """
    # Extract token from credentials
    token = credentials.credentials
    
    # Decode the token
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract student_number from token payload
    # JWT standard uses "sub" (subject) for the user identifier
    student_number: str = payload.get("sub")
    if student_number is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create TokenData object (for type safety)
    token_data = TokenData(student_number=student_number)
    
    # Retrieve student from database
    student = db.query(Student).filter(
        Student.student_number == token_data.student_number
    ).first()
    
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Student not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return student
