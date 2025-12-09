"""
Test data setup utilities for Locust tests.
Provides functions to ensure test data exists in the database.
"""

import os
import random
import string
from datetime import datetime, timedelta, timezone
from typing import Optional
from locust import HttpUser


def generate_student_number(prefix: str = "TEST") -> str:
    """
    Generate a unique test student number.
    
    Args:
        prefix: Prefix for student number (default: "TEST")
    
    Returns:
        Unique student number string
    """
    random_suffix = ''.join(random.choices(string.digits, k=6))
    return f"{prefix}{random_suffix}"


def generate_password(length: int = 12) -> str:
    """
    Generate a random password for test users.
    
    Args:
        length: Password length (default: 12)
    
    Returns:
        Random password string
    """
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))


def create_test_student(
    client: HttpUser,
    student_number: Optional[str] = None,
    password: Optional[str] = None,
    name: Optional[str] = None
) -> tuple[str, str]:
    """
    Create a test student via API (if endpoint exists) or return credentials.
    
    Note: This assumes test students are pre-seeded or created via scripts.
    For Locust tests, we typically use pre-existing test data.
    
    Args:
        client: Locust HttpUser client instance
        student_number: Optional student number (generated if not provided)
        password: Optional password (generated if not provided)
        name: Optional name (generated if not provided)
    
    Returns:
        Tuple of (student_number, password)
    """
    if not student_number:
        student_number = generate_student_number()
    if not password:
        password = generate_password()
    if not name:
        name = f"Test Student {student_number}"
    
    # In a real scenario, you might have a test data creation endpoint
    # For now, we assume test data is pre-seeded
    return student_number, password


def _is_registration_window_open(semester: dict) -> bool:
    """
    Check if the semester registration window is currently open.
    """
    now = datetime.now(timezone.utc)
    start = datetime.fromisoformat(semester["registration_start"])
    end = datetime.fromisoformat(semester["registration_end"])
    return start <= now <= end


def get_test_semester_id(client: HttpUser, token: Optional[str] = None) -> Optional[str]:
    """
    Get an active semester ID from the API (prefers open registration window).
    
    Args:
        client: Locust HttpUser client instance
        token: Optional JWT token for authenticated requests
    
    Returns:
        Semester ID as string, or None if not found
    """
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    response = client.get("/semesters/", headers=headers, name="Get Semesters")
    
    if response.status_code == 200:
        semesters = response.json()
        if not semesters:
            return None
        # Prefer a semester with an open registration window
        open_semesters = [s for s in semesters if _is_registration_window_open(s)]
        target = open_semesters[0] if open_semesters else semesters[0]
        return str(target["id"])
    
    return None


def get_test_course_ids(
    client: HttpUser,
    semester_id: str,
    token: Optional[str] = None,
    limit: Optional[int] = None
) -> list[str]:
    """
    Get test course IDs for a semester.
    
    Args:
        client: Locust HttpUser client instance
        semester_id: Semester ID to get courses for
        token: Optional JWT token for authenticated requests
        limit: Optional limit on number of courses to return
    
    Returns:
        List of course IDs as strings
    """
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    response = client.get(
        f"/semesters/{semester_id}/courses",
        headers=headers,
        name="Get Courses"
    )
    
    if response.status_code == 200:
        courses = response.json()
        course_ids = [str(course["id"]) for course in courses]
        if limit:
            return course_ids[:limit]
        return course_ids
    
    return []


def get_random_course_id(
    client: HttpUser,
    semester_id: str,
    token: Optional[str] = None
) -> Optional[str]:
    """
    Get a random course ID for a semester.
    
    Args:
        client: Locust HttpUser client instance
        semester_id: Semester ID to get courses for
        token: Optional JWT token for authenticated requests
    
    Returns:
        Random course ID as string, or None if not found
    """
    course_ids = get_test_course_ids(client, semester_id, token)
    if course_ids:
        import random
        return random.choice(course_ids)
    return None

