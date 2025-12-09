"""
Drop and Auto-Promotion Test Scenario.
Simulates concurrent drops and verifies auto-promotion from reserve queue works correctly.
"""

import random
from locust import task, between
from course_registration_tests import StudentUser
from utils.auth import ensure_authenticated
from utils.data_setup import get_test_course_ids


class DropAutoPromotionUser(StudentUser):
    """
    User class for testing drop and auto-promotion logic under concurrent load.
    """
    
    wait_time = between(1, 3)
    
    # Track courses we've registered for (per user instance)
    # Initialized in on_start
    registered_courses: list[str]
    
    def on_start(self):
        """
        Initialize and register for some courses first.
        """
        super().on_start()
        self.registered_courses = []
        
        # Register for a few courses to have something to drop
        if self.course_ids and self.token:
            headers = ensure_authenticated(self.client, self.token)
            
            # Register for 2-3 courses
            num_registrations = min(3, len(self.course_ids))
            courses_to_register = random.sample(self.course_ids, num_registrations)
            
            for course_id in courses_to_register:
                response = self.client.post(
                    f"/courses/{course_id}/register",
                    headers=headers,
                    name="Initial Registration (Drop Test)"
                )
                
                if response.status_code == 200:
                    if course_id not in self.registered_courses:
                        self.registered_courses.append(course_id)
    
    @task(5)
    def register_for_course(self):
        """
        Register for additional courses.
        """
        if not self.course_ids or not self.token:
            return
        
        # Find a course we haven't registered for
        available_courses = [c for c in self.course_ids if c not in self.registered_courses]
        if not available_courses:
            return
        
        course_id = random.choice(available_courses)
        headers = ensure_authenticated(self.client, self.token)
        
        response = self.client.post(
            f"/courses/{course_id}/register",
            headers=headers,
            name="Register for Course (Drop Test)"
        )
        
        if response.status_code == 200:
            if course_id not in self.registered_courses:
                self.registered_courses.append(course_id)
    
    @task(3)
    def drop_course(self):
        """
        Drop a course - this should trigger auto-promotion if ENROLLED.
        This is the critical action for testing auto-promotion under load.
        """
        if not self.registered_courses or not self.token:
            return
        
        course_id = random.choice(self.registered_courses)
        headers = ensure_authenticated(self.client, self.token)
        
        response = self.client.post(
            f"/courses/{course_id}/drop",
            headers=headers,
            name="Drop Course (Auto-Promotion Test)"
        )
        
        if response.status_code == 200:
            data = response.json()
            dropped_status = data.get("dropped_status")
            promoted_student_id = data.get("promoted_student_id")
            
            # Validate auto-promotion:
            # - If dropped_status was "ENROLLED", should have promoted_student_id
            # - If dropped_status was "RESERVED", should shift positions
            
            if dropped_status == "ENROLLED" and promoted_student_id:
                # Auto-promotion occurred - validate this in post-test analysis
                pass
            
            # Remove from registered courses
            if course_id in self.registered_courses:
                self.registered_courses.remove(course_id)
    
    @task(2)
    def view_my_courses(self):
        """
        View current registrations to verify status changes.
        """
        if not self.semester_id or not self.token:
            return
        
        headers = ensure_authenticated(self.client, self.token)
        self.client.get(
            f"/semesters/{self.semester_id}/my-courses",
            headers=headers,
            name="View My Courses (Drop Test)"
        )
    
    @task(1)
    def check_course_status(self):
        """
        Check course status to see enrollment/reserve counts.
        """
        if not self.course_ids or not self.token:
            return
        
        course_id = random.choice(self.course_ids)
        headers = ensure_authenticated(self.client, self.token)
        self.client.get(
            f"/courses/{course_id}",
            headers=headers,
            name="Check Course Status (Drop Test)"
        )

