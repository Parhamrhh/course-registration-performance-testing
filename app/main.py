"""
FastAPI main application entry point.
Sets up the FastAPI app, includes routers, and configures middleware.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base
from app.api.routes import auth, semesters, courses, registrations

# Create database tables (in production, use Alembic migrations instead)
# This is just for initial setup - we'll use Alembic for migrations
# Base.metadata.create_all(bind=engine)

# Initialize FastAPI application
app = FastAPI(
    title="Course Registration System API",
    description="A production-ready backend API for university course registration with concurrency-safe enrollment",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc
)

# Include routers
app.include_router(auth.router)
app.include_router(semesters.router)
app.include_router(courses.router)
app.include_router(registrations.router)

# Configure CORS (Cross-Origin Resource Sharing)
# In production, specify exact origins instead of "*"
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this in production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """
    Root endpoint - API health check.
    """
    return {
        "message": "Course Registration System API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    """
    return {"status": "healthy"}

