"""
Authentication API routes.
Handles login and authentication-related endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.student import Student
from app.auth.schemas import LoginRequest, TokenResponse
from app.auth.utils import verify_password, create_access_token

# Create router for authentication endpoints
router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
    responses={401: {"description": "Unauthorized"}},
)


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Student login endpoint.
    
    Authenticates a student using student_number and password.
    Returns a JWT token for subsequent authenticated requests.
    
    Process:
    1. Find student by student_number
    2. Verify password against stored hash
    3. Generate JWT token with student_number as subject
    4. Return token to client
    
    Args:
        login_data: LoginRequest containing student_number and password
        db: Database session (injected by FastAPI)
    
    Returns:
        TokenResponse with JWT access token
    
    Raises:
        HTTPException: 401 if credentials are invalid
    """
    # Find student by student_number
    student = db.query(Student).filter(
        Student.student_number == login_data.student_number
    ).first()
    
    # Check if student exists
    if not student:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect student number or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(login_data.password, student.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect student number or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create JWT token
    # Using student_number as the subject (sub) claim
    access_token = create_access_token(
        data={"sub": student.student_number}
    )
    
    # Return token response
    return TokenResponse(access_token=access_token, token_type="bearer")
