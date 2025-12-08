import argparse
import sys
import random
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Dict, Optional, List, Tuple

import requests

DEFAULT_PASSWORD = "test123"
# Use 10 students for the randomized scenario
DEFAULT_STUDENTS = [f"STU{i:03d}" for i in range(1, 11)]
TIMEOUT = 10


@dataclass
class StudentSession:
    student_number: str
    token: str


# --- API Call Functions ---

def login(host: str, student_number: str, password: str) -> StudentSession:
    """Logs in a student and returns their session token."""
    resp = requests.post(
        f"{host}/auth/login",
        json={"student_number": student_number, "password": password},
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    return StudentSession(student_number=student_number, token=resp.json()["access_token"])


def register(host: str, session: StudentSession, course_id: str):
    """Attempts to register a student for a course."""
    resp = requests.post(
        f"{host}/courses/{course_id}/register",
        headers={"Authorization": f"Bearer {session.token}"},
        timeout=TIMEOUT,
    )
    # Return (student_number, status_code, JSON/Text body)
    return session.student_number, resp.status_code, resp.json() if resp.status_code == 200 else resp.text


def drop(host: str, session: StudentSession, course_id: str):
    """Attempts to drop a student from a course."""
    resp = requests.post(
        f"{host}/courses/{course_id}/drop",
        headers={"Authorization": f"Bearer {session.token}"},
        timeout=TIMEOUT,
    )
    # Return (student_number, status_code, JSON/Text body)
    return session.student_number, resp.status_code, resp.text


# --- Status and Logging Functions ---

def get_status(host: str, session: StudentSession, semester_id: str, course_id: str):
    """Retrieves the registration status for a student in a course."""
    resp = requests.get(
        f"{host}/semesters/{semester_id}/my-courses",
        headers={"Authorization": f"Bearer {session.token}"},
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    courses = resp.json()
    for c in courses:
        if c["course_id"] == course_id:
            return c["status"], c.get("reserve_position")
    return None, None  # not registered


def get_all_statuses(host: str, sessions: Dict[str, StudentSession], semester_id: str, course_id: str):
    """Retrieves and returns the status for all students."""
    current_statuses = {}
    for stu, session in sessions.items():
        status, pos = get_status(host, session, semester_id, course_id)
        current_statuses[stu] = {"status": status, "reserve_position": pos}
    return current_statuses


def print_statuses(statuses: Dict[str, Dict[str, Optional[int]]], title: str):
    """Prints the current status of all students in a formatted table."""
    print(f"\n--- 📊 {title} ---")
    print(f"{'Student':<8} | {'Status':<10} | {'Reserve Pos':<11}")
    print("-" * 34)
    # Sort by status, then reserve position
    sorted_students = sorted(
        statuses.keys(),
        key=lambda s: (
            statuses[s]["status"] or "Z",
            statuses[s]["reserve_position"] if statuses[s]["reserve_position"] is not None else 999
        )
    )
    for stu in sorted_students:
        status = statuses[stu]['status'] or 'none'
        pos = statuses[stu]['reserve_position'] if statuses[stu]['reserve_position'] is not None else ''
        print(f"{stu:<8} | {status:<10} | {str(pos):<11}")
    print("-" * 34)


# --- Assertion Function ---

def assert_reserve_queue_integrity(statuses: Dict[str, Dict[str, Optional[int]]], iteration: int):
    """
    Asserts that the reserve positions are contiguous (1, 2, 3...)
    to check for correct queue management under concurrent load.
    """
    reserved_positions = [
        data['reserve_position']
        for data in statuses.values()
        if data['status'] == 'RESERVED' and data['reserve_position'] is not None
    ]
    
    # Sort the positions to check for gaps
    reserved_positions.sort()
    
    max_pos = len(reserved_positions)
    
    # Check if the list of positions is exactly [1, 2, ..., max_pos]
    expected_positions = list(range(1, max_pos + 1))
    
    error_msg = (
        f"🚨 **Assertion Failed** in Iteration {iteration}: Reserve Queue Integrity Check.\n"
        f"Expected Reserve Positions: {expected_positions}\n"
        f"Actual Reserve Positions: {reserved_positions}"
    )
    
    # Use standard assert for explicit failure stop
    assert reserved_positions == expected_positions, error_msg
    
    print(f"✅ Reserve Queue Integrity Passed in Iteration {iteration} (Length: {max_pos}).")


# --- Main Logic ---

def run_concurrent_scenario(
    host: str,
    sessions: Dict[str, StudentSession],
    semester_id: str,
    course_id: str,
    iterations: int = 3,
):
    # Hardcoded capacities based on the test scenario (Concurrent Systems: cap 2, reserve 2)
    COURSE_CAPACITY = 2       
    RESERVE_CAPACITY = 2      
    
    student_numbers = list(sessions.keys())
    
    # 0. Cleanup
    print("--- 0. Cleanup: Dropping course for all students (ignoring errors) ---")
    for stu in student_numbers:
        drop(host, sessions[stu], course_id)
    time.sleep(0.5)

    for i in range(1, iterations + 1):
        print(f"\n\n#####################################################")
        print(f"## 🔄 Starting Concurrent Iteration **{i}** of **{iterations}**")
        print(f"#####################################################")
        
        current_statuses = get_all_statuses(host, sessions, semester_id, course_id)
        print_statuses(current_statuses, f"Iteration {i} - Initial State")

        # --- 1. Concurrent Randomized Registration Attempts ---
        
        students_to_register = [
            s for s, data in current_statuses.items()
            if data['status'] is None
        ]
        # Only select a random subset (up to 70%) to attempt to register
        num_to_register = random.randint(1, int(len(students_to_register) * 0.7) or 1)
        register_attempts_sessions = random.sample([sessions[s] for s in students_to_register], num_to_register)
        
        print(f"\n--- 1. Concurrent Registration Attempts ({len(register_attempts_sessions)} students) ---")
        
        with ThreadPoolExecutor(max_workers=len(register_attempts_sessions)) as executor:
            futures = [
                executor.submit(register, host, s, course_id)
                for s in register_attempts_sessions
            ]
            for fut in as_completed(futures):
                stu, status_code, body = fut.result()
                if status_code == 200:
                    status = body.get('status', 'ENROLLED/RESERVED')
                    pos = body.get('reserve_position', 'N/A')
                    print(f"✅ **{stu}** registered. Status: **{status}**, Pos: {pos}")
                else:
                    if status_code in (400, 409):
                        print(f"⚠️ **{stu}** failed as expected (Code: {status_code}).")
                    else:
                        assert False, f"🚨 Unexpected Status Code {status_code} for {stu} registration: {body}"
        time.sleep(0.5)
        
        # --- 2. Concurrent Randomized Drop Attempts ---
        
        current_statuses = get_all_statuses(host, sessions, semester_id, course_id)
        students_to_drop = [
            s for s, data in current_statuses.items()
            if data['status'] in ('ENROLLED', 'RESERVED')
        ]
        
        # Only select a random subset (up to 40%) to attempt to drop
        num_to_drop = random.randint(1, int(len(students_to_drop) * 0.4) or 1)
        drop_attempts_sessions = random.sample([sessions[s] for s in students_to_drop], num_to_drop)
        
        print(f"\n--- 2. Concurrent Drop Attempts ({len(drop_attempts_sessions)} students) ---")
        
        with ThreadPoolExecutor(max_workers=len(drop_attempts_sessions)) as executor:
            futures = [
                executor.submit(drop, host, s, course_id)
                for s in drop_attempts_sessions
            ]
            for fut in as_completed(futures):
                stu, status_code, body = fut.result()
                if status_code == 200:
                    print(f"✅ **{stu}** dropped successfully.")
                else:
                    print(f"⚠️ **{stu}** drop failed (Code: {status_code}). Response: {body.strip()[:50]}...")
        time.sleep(0.5)
        
        # --- 3. Final Assertion and State Print for Iteration ---

        # If this is the LAST ITERATION, force the reserve queue to be full.
        if i == iterations:
            print("\n--- 3A. Forcing Reserve Queue to Full Capacity for Final Stress Test ---")
            
            # Find the state: How many enrolled/reserved spots are available?
            current_statuses = get_all_statuses(host, sessions, semester_id, course_id)
            enrolled_count = sum(1 for data in current_statuses.values() if data['status'] == 'ENROLLED')
            reserved_count = sum(1 for data in current_statuses.values() if data['status'] == 'RESERVED')
            
            # Calculate how many students we need to register to fill the reserve list
            total_slots = COURSE_CAPACITY + RESERVE_CAPACITY
            needed_to_register = total_slots - (enrolled_count + reserved_count)
            
            students_not_in_course = [
                s for s, data in current_statuses.items()
                if data['status'] is None
            ]
            
            if needed_to_register > 0 and len(students_not_in_course) >= needed_to_register:
                students_to_force_fill = students_not_in_course[:needed_to_register]
                
                print(f"   - Needs {needed_to_register} more registration(s) to fill reserve queue.")
                
                fill_sessions = [sessions[s] for s in students_to_force_fill]
                with ThreadPoolExecutor(max_workers=len(fill_sessions)) as executor:
                    futures = [
                        executor.submit(register, host, s, course_id)
                        for s in fill_sessions
                    ]
                    for fut in as_completed(futures):
                        stu, status_code, body = fut.result()
                        if status_code == 200:
                            print(f"   - ✅ **{stu}** forced to register.")
                        else:
                            assert False, f"🚨 FATAL: Force-fill registration failed for {stu} with code {status_code}: {body}"

            elif needed_to_register <= 0:
                print("   - Reserve queue is already full or overfilled, skipping force-fill.")
            else:
                print(f"   - Cannot force fill reserve queue: Only {len(students_not_in_course)} students available but need {needed_to_register}.")

        
        # --- 3B. Final Assertion and State Print for Iteration ---
        
        final_statuses = get_all_statuses(host, sessions, semester_id, course_id)
        print_statuses(final_statuses, f"Iteration {i} - Final State for Assertion")
        
        # ASSERTER 1: Check if the reserve queue positions are contiguous (1, 2, 3...)
        assert_reserve_queue_integrity(final_statuses, i)
        
        # ASSERTER 2: FINAL CHECK for the LAST ITERATION: Ensure the reserve queue is full
        if i == iterations:
            reserved_count = sum(1 for data in final_statuses.values() if data['status'] == 'RESERVED')
            assert reserved_count == RESERVE_CAPACITY, f"🚨 FINAL ITERATION FAILED: Expected reserve count of {RESERVE_CAPACITY} but got {reserved_count}"
            print(f"✅ FINAL CHECK PASSED: Reserve queue is full ({reserved_count}/{RESERVE_CAPACITY}).")

        print(f"\n✅ **Iteration {i} completed and assertions passed.**")


def main():
    parser = argparse.ArgumentParser(description="Assert-driven Concurrent & Randomized Registration/Drop Test")
    parser.add_argument("--host", default="http://localhost:8500", help="API host")
    parser.add_argument("--semester-id", required=True, help="Semester UUID (needed for status check)")
    parser.add_argument("--course-id", required=True, help="Course UUID to target")
    parser.add_argument(
        "--students",
        nargs="+",
        default=DEFAULT_STUDENTS,
        help="List of student_numbers to use (defaults to STU001-STU010)",
    )
    parser.add_argument(
        "--password",
        default=DEFAULT_PASSWORD,
        help="Password for all test students",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=3,
        help="Number of randomized concurrent iterations to run",
    )
    args = parser.parse_args()

    # --- Login ---
    print(f"--- Logging in {len(args.students)} students... ---")
    sessions_map: Dict[str, StudentSession] = {}
    try:
        for stu in args.students:
            session = login(args.host, stu, args.password)
            sessions_map[stu] = session
            print(f"  - Logged in {stu}")
    except Exception as e:
        print(f"🚨 Login failed for a student. Ensure host is correct and seed data is loaded: {e}")
        sys.exit(1)
    
    # Run the concurrent and randomized scenario (Capacity is hardcoded internally)
    run_concurrent_scenario(
        args.host, sessions_map, args.semester_id, args.course_id, 
        args.iterations
    )

    print(f"\n\n#####################################################")
    print("**All randomized concurrent assertions passed successfully.**")
    print(f"#####################################################")    

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)
    except AssertionError as e:
        print(f"\n\n🛑 **TEST FAILED.**")
        print(e)
        sys.exit(1)