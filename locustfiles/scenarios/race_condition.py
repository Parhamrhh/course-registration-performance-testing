"""
Race Condition Test Scenario.
All users attempt to register for the SAME course simultaneously to test concurrency safety.
"""

import random
from locust import task, between
from course_registration_tests import StudentUser
from utils.auth import ensure_authenticated
from utils.data_setup import get_test_course_ids


class RaceConditionUser(StudentUser):
    """
    User class for race condition testing.
    All users will attempt to register for the same target course.
    """
    
    wait_time = between(0.5, 1.5)  # Faster actions to create more contention
    
    # Class-level variable to store target course ID
    # This will be set once and shared across all users
    target_course_id = None
    
    def on_start(self):
        """
        Initialize and set the target course for race condition testing.
        """
        super().on_start()
        
        # Set target course ID if not already set
        # All users will compete for this same course
        if RaceConditionUser.target_course_id is None and self.course_ids:
            RaceConditionUser.target_course_id = random.choice(self.course_ids)
            print(f"Race condition test: Target course ID = {RaceConditionUser.target_course_id}")
    
    @task(10)
    def attempt_registration(self):
        """
        Attempt to register for the target course.
        This is the critical action - all users compete for the same course.
        """
        if not RaceConditionUser.target_course_id or not self.token:
            return
        
        headers = ensure_authenticated(self.client, self.token)
        
        response = self.client.post(
            f"/courses/{RaceConditionUser.target_course_id}/register",
            headers=headers,
            name="Race Condition Registration"
        )
        
        # Track results for validation
        if response.status_code == 200:
            data = response.json()
            status = data.get("status")
            # In a real test, we'd validate:
            # - Exactly max_capacity users got ENROLLED
            # - Up to reserve_limit users got RESERVED
            # - No capacity overflow occurred
        elif response.status_code == 409:
            # Expected: Course full or already registered
            pass
    
    @task(1)
    def check_course_status(self):
        """
        Check the status of the target course.
        """
        if not RaceConditionUser.target_course_id or not self.token:
            return
        
        headers = ensure_authenticated(self.client, self.token)
        self.client.get(
            f"/courses/{RaceConditionUser.target_course_id}",
            headers=headers,
            name="Check Target Course Status"
        )

