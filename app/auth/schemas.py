"""
Pydantic schemas for authentication.
Defines request/response models for authentication endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional


class LoginRequest(BaseModel):
    """
    Request schema for login endpoint.
    
    Attributes:
        student_number: Unique student number (used as username)
        password: Plain text password (will be hashed and compared)
    """
    student_number: str = Field(..., description="Student number for login")
    password: str = Field(..., min_length=1, description="Student password")


class TokenResponse(BaseModel):
    """
    Response schema for successful login.
    
    Attributes:
        access_token: JWT token for authenticated requests
        token_type: Type of token (always "bearer" for JWT)
    """
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")


class TokenData(BaseModel):
    """
    Decoded token data structure.
    Used internally to represent the data extracted from a JWT token.
    
    Attributes:
        student_number: Student number extracted from token
    """
    student_number: Optional[str] = None
