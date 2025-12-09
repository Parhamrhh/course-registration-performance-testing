"""
Peak Registration Load Scenario.
Simulates normal high-load registration with multiple users registering for different courses.
"""

import random
from locust import task, between
from course_registration_tests import StudentUser
from utils.auth import ensure_authenticated
from utils.data_setup import get_random_course_id


class PeakRegistrationUser(StudentUser):
    """
    User class for peak registration load testing.
    Simulates realistic registration behavior with browsing and registering.
    """
    
    wait_time = between(2, 5)  # More realistic wait times

    def on_start(self):
        """
        Initialize user state and caches.
        """
        super().on_start()
        # Track courses this user successfully registered for
        self.registered_courses: list[str] = []
    
    @task(5)
    def browse_courses(self):
        """
        Browse available courses (most common action).
        """
        if not self.semester_id or not self.token:
            return
        
        headers = ensure_authenticated(self.client, self.token)
        self.client.get(
            f"/semesters/{self.semester_id}/courses",
            headers=headers,
            name="Browse Courses"
        )
    
    @task(3)
    def view_course_details(self):
        """
        View details of a specific course.
        """
        if not self.course_ids or not self.token:
            return
        
        course_id = random.choice(self.course_ids)
        headers = ensure_authenticated(self.client, self.token)
        self.client.get(
            f"/courses/{course_id}",
            headers=headers,
            name="View Course Details"
        )
    
    @task(2)
    def register_for_course(self):
        """
        Register for a random course.
        This is the main action we're testing under load.
        """
        if not self.course_ids or not self.token:
            return
        
        course_id = random.choice(self.course_ids)
        headers = ensure_authenticated(self.client, self.token)
        
        response = self.client.post(
            f"/courses/{course_id}/register",
            headers=headers,
            name="Register for Course"
        )
        
        # Log registration result for analysis
        if response.status_code == 200:
            data = response.json()
            status = data.get("status", "UNKNOWN")
            # Could log metrics here: ENROLLED vs RESERVED
            # Track successful registration to allow valid drops later
            if course_id not in self.registered_courses:
                self.registered_courses.append(course_id)
        elif response.status_code == 409:
            # Course full or already registered - expected in load tests
            pass
    
    @task(1)
    def view_my_registrations(self):
        """
        Check current registrations.
        """
        if not self.semester_id or not self.token:
            return
        
        headers = ensure_authenticated(self.client, self.token)
        self.client.get(
            f"/semesters/{self.semester_id}/my-courses",
            headers=headers,
            name="View My Registrations"
        )
    
    @task(1)
    def drop_course(self):
        """
        Occasionally drop a course (less frequent than registration).
        """
        if not self.registered_courses or not self.token:
            return
        
        # Only drop a course we have actually registered for
        course_id = random.choice(self.registered_courses)
        headers = ensure_authenticated(self.client, self.token)
        
        response = self.client.post(
            f"/courses/{course_id}/drop",
            headers=headers,
            name="Drop Course"
        )
        if response.status_code == 200:
            # Remove from tracked registrations
            self.registered_courses = [
                cid for cid in self.registered_courses if cid != course_id
            ]

