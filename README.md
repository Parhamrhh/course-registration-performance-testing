# Course Registration System

A production-ready backend API for a university Semester-Based Course Registration System with concurrency-safe course enrollment and waiting list (reserve list) logic.

## Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **Authentication**: JWT with bcrypt
- **Performance Testing**: Locust
- **Containerization**: Docker & Docker Compose


## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Git (optional)

### Setup

1. **Clone the repository** (if applicable):
   ```bash
   git clone https://github.com/Parhamrhh/course-registration-performance-testing.git
   cd course-registration
   ```

2. **Create environment file** (optional, defaults are set):
   ```bash
   cp .env.example .env
   # Edit .env with your configuration if needed
   ```

3. **Start all services**:
   ```bash
   docker-compose up --build
   ```

   This will start:
   - PostgreSQL database (port 5432)
   - FastAPI application (port 8500)
   - Locust master (port 8585)
   - Locust worker

4. **Run database migrations**:
   ```bash
   docker-compose exec api alembic upgrade head
   ```

5. **Seed data (students, semesters, courses)**:
   ```bash
   # 1,000 students STU10000–STU10999, password: test123
   docker-compose exec api python scripts/seed_students.py
   # Additional semesters
   docker-compose exec api python scripts/seed_semesters.py
   # Additional courses
   docker-compose exec api python scripts/seed_courses.py
   ```

5. **Access the services**:
   - API: http://localhost:8500
   - API Docs (Swagger): http://localhost:8500/docs
   - API Docs (ReDoc): http://localhost:8500/redoc
   - Locust UI: http://localhost:8585

## Development

### Running Migrations

```bash
# Create a new migration
docker-compose exec api alembic revision --autogenerate -m "description"

# Apply migrations
docker-compose exec api alembic upgrade head

# Rollback migration
docker-compose exec api alembic downgrade -1
```

### Database Access

```bash
# Connect to PostgreSQL
docker-compose exec db psql -U postgres -d course_registration
```

### Viewing Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f db
```

## API Endpoints

### Authentication
- `POST /auth/login` - Student login

### Semesters
- `GET /semesters/` - List all semesters
- `GET /semesters/{id}` - Get semester details

### Courses
- `GET /semesters/{id}/courses` - List courses for a semester
- `GET /courses/{id}` - Get course details

### Registrations
- `GET /semesters/{id}/my-courses` - Get student's courses
- `POST /courses/{course_id}/register` - Register for a course
- `POST /courses/{course_id}/drop` - Drop a course

## Database Schema

### Students
- `id` (UUID, PK)
- `student_number` (String, Unique)
- `password_hash` (String)
- `name` (String)
- `created_at`, `updated_at` (Timestamps)

### Semesters
- `id` (UUID, PK)
- `name` (String)
- `registration_start` (Timestamp)
- `registration_end` (Timestamp)
- `created_at`, `updated_at` (Timestamps)

### Courses
- `id` (UUID, PK)
- `semester_id` (UUID, FK)
- `course_name` (String)
- `professor` (String)
- `schedule` (String)
- `max_capacity` (Integer)
- `reserve_limit` (Integer, default=10)
- `created_at`, `updated_at` (Timestamps)

### Course Registrations
- `id` (UUID, PK)
- `student_id` (UUID, FK)
- `course_id` (UUID, FK)
- `status` (ENUM: "ENROLLED" or "RESERVED")
- `reserve_position` (Integer, NULL if ENROLLED)
- `created_at`, `updated_at` (Timestamps)
- **Constraint**: UNIQUE(student_id, course_id)

## Performance Testing (Locust)

- Locust UI: http://localhost:8585
- Headless runner (presets):  
  ```bash
  cd locustfiles
  ./scripts/run_tests.sh load --headless        # normal load
  ./scripts/run_tests.sh stress --headless      # stress
  ./scripts/run_tests.sh spike --headless       # spike
  ./scripts/run_tests.sh soak --headless        # soak
  ```
- Custom mixes (class_picker aliases): `StudentUser, PeakLoadUser, RaceUser, ReserveQueueUser, DropPromotionUser`
  ```bash
  locust -f locustfiles/course_registration_tests.py \
    --class-picker "StudentUser:1,PeakLoadUser:2,RaceUser:2,ReserveQueueUser:2,DropPromotionUser:1" \
    --host=http://api:8500 --headless --users 100 --spawn-rate 10 --run-time 10m
  ```
- Custom metrics (p95/p99, RPS, error rate) are logged at test end (`Custom Metrics Summary: {...}`).

## Environment Variables

See `.env.example` for all available configuration options.

Key variables:
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT secret key (change in production!)
- `ALGORITHM` - JWT algorithm (default HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - JWT token expiration time
- `ENVIRONMENT` - environment name (default development)
