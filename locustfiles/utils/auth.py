"""
Authentication utilities for Locust tests.
Handles JWT token management for test users.
"""

import os
from typing import Optional
from locust import HttpUser


def login_user(client: HttpUser, student_number: str, password: str) -> Optional[str]:
    """
    Login a user and return JWT token.
    
    Args:
        client: Locust HttpUser client instance
        student_number: Student number for login
        password: Password for login
    
    Returns:
        JWT access token if login successful, None otherwise
    """
    response = client.post(
        "/auth/login",
        json={
            "student_number": student_number,
            "password": password
        },
        name="Login"
    )
    
    if response.status_code == 200:
        data = response.json()
        return data.get("access_token")

    if response.status_code == 401:
        print(f"Login failed (401) for {student_number}. Check password hash mismatch.")
    
    return None


def get_auth_headers(token: str) -> dict:
    """
    Get authorization headers for authenticated requests.
    
    Args:
        token: JWT access token
    
    Returns:
        Dictionary with Authorization header
    """
    return {
        "Authorization": f"Bearer {token}"
    }


def ensure_authenticated(client: HttpUser, token: Optional[str]) -> dict:
    """
    Ensure request headers include authentication if token is available.
    
    Args:
        client: Locust HttpUser client instance
        token: Optional JWT token
    
    Returns:
        Headers dictionary with authentication if token provided
    """
    if token:
        return get_auth_headers(token)
    return {}

