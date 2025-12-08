"""
Authentication utility functions.
Handles password hashing (bcrypt) and JWT token operations.
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.hash import bcrypt_sha256
from app.config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a bcrypt hash.
    
    Args:
        plain_password: The plain text password to verify
        hashed_password: The bcrypt hash to compare against
    
    Returns:
        True if password matches, False otherwise
    """
    return bcrypt_sha256.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    This function should be used when creating or updating a user's password.
    Never store plain text passwords in the database!
    
    Args:
        password: The plain text password to hash
    
    Returns:
        The bcrypt hash of the password
    """
    return bcrypt_sha256.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    JWT tokens contain encoded information (claims) that can be verified
    without needing to query the database. This makes them stateless and scalable.
    
    Args:
        data: Dictionary containing the data to encode in the token (e.g., {"sub": student_number})
        expires_delta: Optional custom expiration time. If None, uses default from settings.
    
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    # Add expiration to token data
    to_encode.update({"exp": expire})
    
    # Encode the token using the secret key and algorithm
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and verify a JWT access token.
    
    Args:
        token: The JWT token string to decode
    
    Returns:
        Dictionary containing the decoded token data if valid, None otherwise
    """
    try:
        # Decode and verify the token
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        return payload
    except JWTError:
        # Token is invalid, expired, or malformed
        return None
