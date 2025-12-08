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

## Project Structure

```
course-registration/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py             # Configuration management
│   ├── database.py           # Database connection and session management
│   ├── models/               # SQLAlchemy database models
│   │   ├── student.py
│   │   ├── semester.py
│   │   ├── course.py
│   │   └── course_registration.py
│   ├── auth/                 # Authentication module (Phase 2)
│   ├── api/                   # API routes (Phase 3-4)
│   ├── schemas/               # Pydantic schemas (Phase 3-4)
│   └── services/              # Business logic (Phase 4)
├── alembic/                   # Database migrations
│   └── versions/
├── locustfiles/               # Locust performance tests (Phase 6-7)
├── requirements.txt           # Python dependencies
├── Dockerfile                 # API service container
├── docker-compose.yml         # Multi-service orchestration
└── README.md                  # This file
```

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Git (optional)

### Setup

1. **Clone the repository** (if applicable):
   ```bash
   git clone <repository-url>
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

5. **Seed a test student (STU001 / test123)**:
   ```bash
   docker-compose exec api python scripts/seed_student.py
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

### Authentication (Phase 2)
- `POST /auth/login` - Student login

### Semesters (Phase 3)
- `GET /semesters/` - List all semesters
- `GET /semesters/{id}` - Get semester details

### Courses (Phase 3)
- `GET /semesters/{id}/courses` - List courses for a semester
- `GET /courses/{id}` - Get course details

### Registrations (Phase 3-4)
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

## Performance Testing

Locust performance tests will be available in Phase 6-7. Access the Locust UI at http://localhost:8585 once services are running.

## Environment Variables

See `.env.example` for all available configuration options.

Key variables:
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT secret key (change in production!)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - JWT token expiration time

## License

[Your License Here]

