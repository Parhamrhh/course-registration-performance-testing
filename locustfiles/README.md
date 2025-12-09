# Locust Performance Testing Guide

This directory contains Locust performance tests for the Course Registration System.

## Overview

The Locust tests are designed to validate the system's performance, concurrency safety, and scalability under various load conditions. Tests are organized into scenarios that simulate different usage patterns.

## File Structure

```
locustfiles/
├── course_registration_tests.py  # Main test file (referenced in docker-compose.yml)
├── scenarios/                     # Test scenario modules
│   ├── peak_registration.py       # Normal high-load registration
│   ├── race_condition.py          # Concurrent registration for same course
│   ├── reserve_queue_pressure.py  # Reserve queue testing
│   └── drop_auto_promotion.py     # Drop and auto-promotion testing
├── utils/                         # Utility modules
│   ├── auth.py                    # JWT authentication helpers
│   └── data_setup.py              # Test data utilities
└── README.md                      # This file
```

## Running Tests

### Using Docker Compose (Recommended)

The Locust master and worker services are already configured in `docker-compose.yml`:

```bash
# Start all services including Locust
docker-compose up

# Access Locust UI
# Open http://localhost:8585 in your browser
```

### Manual Execution

If running Locust manually:

```bash
# Install dependencies
pip install -r requirements.txt

# Run Locust (single process)
locust -f locustfiles/course_registration_tests.py --host=http://localhost:8500

# Run in distributed mode (master)
locust -f locustfiles/course_registration_tests.py --master --host=http://localhost:8500

# Run in distributed mode (worker)
locust -f locustfiles/course_registration_tests.py --worker --master-host=localhost
```

## Test Scenarios

### 1. Peak Registration Load (`peak_registration.py`)

**Purpose**: Simulate normal high-load registration with realistic user behavior.

**Behavior**:
- Users browse courses (most common action)
- Users view course details
- Users register for random courses
- Users occasionally drop courses
- Users check their registrations

**Use Case**: Validate system performance under normal production load.

**How to Run**:
Modify `course_registration_tests.py` to use `PeakRegistrationUser`:
```python
from locustfiles.scenarios.peak_registration import PeakRegistrationUser

class StudentUser(PeakRegistrationUser):
    pass
```

### 2. Race Condition Test (`race_condition.py`)

**Purpose**: Test concurrency safety when all users attempt to register for the same course simultaneously.

**Behavior**:
- All users target the same course ID
- High-frequency registration attempts
- Validates capacity limits are never exceeded

**Use Case**: Critical for validating that database locking prevents race conditions.

**How to Run**:
Modify `course_registration_tests.py` to use `RaceConditionUser`:
```python
from locustfiles.scenarios.race_condition import RaceConditionUser

class StudentUser(RaceConditionUser):
    pass
```

**Validation**: After test, verify:
- Exactly `max_capacity` students are ENROLLED
- Up to `reserve_limit` students are RESERVED
- No capacity overflow occurred

### 3. Reserve Queue Pressure (`reserve_queue_pressure.py`)

**Purpose**: Test reserve queue logic when courses are at capacity.

**Behavior**:
- Users attempt to register for a target course
- Course fills to capacity (ENROLLED)
- Additional registrations go to reserve queue (RESERVED)
- Validates reserve position assignment

**Use Case**: Ensure reserve queue maintains correct order and positions.

**How to Run**:
Modify `course_registration_tests.py` to use `ReserveQueuePressureUser`:
```python
from locustfiles.scenarios.reserve_queue_pressure import ReserveQueuePressureUser

class StudentUser(ReserveQueuePressureUser):
    pass
```

### 4. Drop and Auto-Promotion (`drop_auto_promotion.py`)

**Purpose**: Test concurrent drops and verify auto-promotion from reserve queue works correctly.

**Behavior**:
- Users register for courses initially
- Users drop courses concurrently
- Validates auto-promotion when ENROLLED courses are dropped
- Validates position shifting when RESERVED courses are dropped

**Use Case**: Critical for validating reserve queue promotion logic under load.

**How to Run**:
Modify `course_registration_tests.py` to use `DropAutoPromotionUser`:
```python
from locustfiles.scenarios.drop_auto_promotion import DropAutoPromotionUser

class StudentUser(DropAutoPromotionUser):
    pass
```

## Configuration

### Test Data Requirements

Before running tests, ensure test data exists:

1. **Test Students**: Create test students with known credentials
   - Default password: `test123`
   - Student numbers: `TEST100000` to `TEST999999` (or use seed script)

2. **Test Semesters**: Create at least one active semester with:
   - `registration_start` in the past
   - `registration_end` in the future
   - Multiple courses with various capacities

3. **Test Courses**: Create courses with:
   - Various `max_capacity` values (e.g., 10, 50, 100)
   - `reserve_limit` values (default: 10)

### Environment Variables

Tests use the API endpoint configured in docker-compose.yml:
- API URL: `http://api:8500` (from within Docker network)
- API URL: `http://localhost:8500` (from host machine)

## Metrics and Analysis

### Key Metrics to Monitor

1. **Response Times**:
   - Average response time
   - p95 latency
   - p99 latency

2. **Throughput**:
   - Requests per second (RPS)
   - Successful registrations per second

3. **Error Rates**:
   - HTTP error rates (4xx, 5xx)
   - Failed authentication attempts
   - Capacity exceeded errors (expected in some scenarios)

4. **Concurrency Validation**:
   - No capacity overflows
   - Reserve queue maintains correct order
   - Auto-promotion works correctly

### Post-Test Validation

After running tests, validate:

1. **Database Integrity**:
   ```sql
   -- Check no capacity overflows
   SELECT course_id, COUNT(*) as enrolled_count, max_capacity
   FROM course_registrations cr
   JOIN courses c ON cr.course_id = c.id
   WHERE cr.status = 'ENROLLED'
   GROUP BY course_id, max_capacity
   HAVING COUNT(*) > max_capacity;
   -- Should return 0 rows
   ```

2. **Reserve Queue Integrity**:
   ```sql
   -- Check reserve positions are sequential
   SELECT course_id, reserve_position, COUNT(*) as count
   FROM course_registrations
   WHERE status = 'RESERVED'
   GROUP BY course_id, reserve_position
   HAVING COUNT(*) > 1;
   -- Should return 0 rows (no duplicate positions)
   ```

## Troubleshooting

### Locust Containers Exit Immediately

**Symptom**: Locust master/worker containers exit with code 1.

**Cause**: `course_registration_tests.py` file not found or has syntax errors.

**Solution**: 
- Verify file exists at `locustfiles/course_registration_tests.py`
- Check for Python syntax errors
- Review container logs: `docker-compose logs locust-master`

### Authentication Failures

**Symptom**: All requests return 401 Unauthorized.

**Cause**: Test students don't exist or have wrong credentials.

**Solution**:
- Seed test students: `docker-compose exec api python scripts/seed_student.py`
- Verify student credentials match test expectations
- Check JWT token generation in `utils/auth.py`

### No Test Data Available

**Symptom**: Tests fail because no semesters/courses exist.

**Solution**:
- Run seed scripts to create test data
- Verify semester registration windows are open (current time between start and end)
- Check database: `docker-compose exec db psql -U postgres -d course_registration`

## Best Practices

1. **Start Small**: Begin with low user counts (10-50 users) and gradually increase.

2. **Monitor Resources**: Watch CPU, memory, and database connection pool usage.

3. **Validate Results**: Always verify database integrity after tests, especially for race condition scenarios.

4. **Use Distributed Mode**: For realistic load testing, use Locust master + worker setup.

5. **Test Data Isolation**: Use separate test data or cleanup between test runs.

6. **Document Scenarios**: Document expected behavior and validation criteria for each scenario.

## Next Steps

- See `docs/PERFORMANCE_TESTING.md` for comprehensive performance testing guide (Phase 7)
- See `docs/API.md` for API endpoint documentation
- See main `README.md` for overall project setup

