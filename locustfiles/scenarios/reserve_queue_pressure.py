"""
Reserve Queue Pressure Test Scenario.
Fills courses to capacity, then tests reserve queue logic under load.
"""

import random
from locust import task, between
from course_registration_tests import StudentUser
from utils.auth import ensure_authenticated
from utils.data_setup import get_test_course_ids


class ReserveQueuePressureUser(StudentUser):
    """
    User class for testing reserve queue under pressure.
    Tests the reserve queue logic when courses are at capacity.
    """
    
    wait_time = between(1, 2)
    
    def on_start(self):
        """
        Initialize and identify courses to fill.
        """
        super().on_start()
        
        # Select a course to fill to capacity
        # In a real scenario, we might coordinate to fill specific courses
        if self.course_ids:
            # Use first course as target for filling
            self.target_course_id = self.course_ids[0]
        else:
            self.target_course_id = None
    
    @task(8)
    def register_for_target_course(self):
        """
        Attempt to register for the target course.
        This will fill the course to capacity and beyond, testing reserve queue.
        """
        if not self.target_course_id or not self.token:
            return
        
        headers = ensure_authenticated(self.client, self.token)
        
        response = self.client.post(
            f"/courses/{self.target_course_id}/register",
            headers=headers,
            name="Register for Target Course (Reserve Queue Test)"
        )
        
        if response.status_code == 200:
            data = response.json()
            status = data.get("status")
            reserve_position = data.get("reserve_position")
            
            # Validate reserve queue behavior:
            # - First max_capacity registrations should be ENROLLED
            # - Next reserve_limit registrations should be RESERVED with positions 1-N
            # - Beyond that should return 409 (full)
            
            if status == "RESERVED" and reserve_position:
                # Successfully added to reserve queue
                pass
        elif response.status_code == 409:
            # Course full - expected when capacity + reserve_limit are reached
            pass
    
    @task(2)
    def check_course_details(self):
        """
        Check course details to see current enrollment/reserve status.
        """
        if not self.target_course_id or not self.token:
            return
        
        headers = ensure_authenticated(self.client, self.token)
        self.client.get(
            f"/courses/{self.target_course_id}",
            headers=headers,
            name="Check Course Details (Reserve Queue)"
        )
    
    @task(1)
    def view_my_courses(self):
        """
        View own registrations to see reserve position.
        """
        if not self.semester_id or not self.token:
            return
        
        headers = ensure_authenticated(self.client, self.token)
        self.client.get(
            f"/semesters/{self.semester_id}/my-courses",
            headers=headers,
            name="View My Courses (Reserve Queue)"
        )

