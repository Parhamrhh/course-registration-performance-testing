"""
Main Locust test file for Course Registration System.
This file is referenced in docker-compose.yml and contains the base test user class.
"""

import random
from locust import HttpUser, task, between
from utils.auth import login_user, ensure_authenticated
from utils.data_setup import (
    get_test_semester_id,
    get_test_course_ids,
    get_random_course_id,
    generate_student_number,
    generate_password,
)


class StudentUser(HttpUser):
    """
    Base Locust user class representing a student using the course registration system.
    
    This class handles authentication and provides base functionality for test scenarios.
    Individual scenarios can inherit from this class or use it as a base.
    """
    
    # Wait between 1 and 3 seconds between tasks
    wait_time = between(1, 3)
    
    def on_start(self):
        """
        Called when a simulated user starts.
        Performs login and stores authentication token.
        """
        # Generate student ID matching seeded format: STU + 5-digit number
        # Seeded students are in range 10000-10999 (1,000 students)
        # This ensures high probability of matching a pre-seeded student
        student_num = random.randint(10000, 10999)
        self.student_number = f"STU{student_num:05d}"  # Format as STU10000, STU10999, etc.
        self.password = "test123"  # Default password for all test users
        
        # Attempt login
        self.token = login_user(self.client, self.student_number, self.password)
        
        if not self.token:
            # If login fails, we might be using a non-existent user
            # In production tests, ensure test users are pre-seeded
            print(f"Warning: Failed to login user {self.student_number}")
        
        # Cache semester and course data for faster access
        self.semester_id = None
        self.course_ids = []
        self._load_test_data()
    
    def _load_test_data(self):
        """
        Load test data (semesters, courses) for use in tests.
        """
        if self.token:
            self.semester_id = get_test_semester_id(self.client, self.token)
            if self.semester_id:
                self.course_ids = get_test_course_ids(self.client, self.semester_id, self.token)
    
    @task(3)
    def view_semesters(self):
        """
        View all available semesters.
        """
        headers = ensure_authenticated(self.client, self.token)
        self.client.get("/semesters/", headers=headers, name="View Semesters")
    
    @task(2)
    def view_courses(self):
        """
        View courses for a semester.
        """
        if not self.semester_id:
            return
        
        headers = ensure_authenticated(self.client, self.token)
        self.client.get(
            f"/semesters/{self.semester_id}/courses",
            headers=headers,
            name="View Courses"
        )
    
    @task(1)
    def view_my_courses(self):
        """
        View the student's registered courses.
        """
        if not self.semester_id or not self.token:
            return
        
        headers = ensure_authenticated(self.client, self.token)
        self.client.get(
            f"/semesters/{self.semester_id}/my-courses",
            headers=headers,
            name="View My Courses"
        )



# from scenarios.peak_registration import PeakRegistrationUser

# class PeakLoadUser(PeakRegistrationUser):
#     """
#     Locust will run this class, which inherits all logic and tasks 
#     from PeakRegistrationUser.
#     """
#     pass


# from scenarios.race_condition import RaceConditionUser

# class RaceUser(RaceConditionUser):
#     """
#     Locust will run this class, which inherits all logic and tasks 
#     from RaceConditionUser.
#     """
#     pass


# from scenarios.reserve_queue_pressure import ReserveQueuePressureUser

# class ReserveQueueUser(ReserveQueuePressureUser):
#     """
#     Locust will run this class, which inherits all logic and tasks 
#     from ReserveQueuePressureUser.
#     """
#     pass


# from scenarios.drop_auto_promotion import DropAutoPromotionUser

# class DropPromotionUser(DropAutoPromotionUser):
#     """
#     Locust will run this class, which inherits all logic and tasks 
#     from DropAutoPromotionUser.
#     """
#     pass

# How to run:
# - Default (only StudentUser): no --class-picker needed.
# - Single scenario: use --class-picker with weight 1, e.g.
#     locust -f locustfiles/course_registration_tests.py \
#       --class-picker "PeakRegistrationUser:1" --host=http://api:8500
# - Mixed scenarios: supply multiple classes with weights, e.g.
#     locust -f locustfiles/course_registration_tests.py \
#       --class-picker "StudentUser:1,PeakRegistrationUser:2,RaceConditionUser:2,ReserveQueuePressureUser:2,DropAutoPromotionUser:1" \
#       --host=http://api:8500
# - Headless example with config: see locustfiles/scripts/run_tests.sh
# or register multiple classes in this file and use --headless --users N --spawn-rate R

