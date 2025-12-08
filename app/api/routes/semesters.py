"""
Semester read-only endpoints.
"""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.semester import Semester
from app.schemas.semester import SemesterBase, SemesterDetail


router = APIRouter(
    prefix="/semesters",
    tags=["semesters"],
)


@router.get("/", response_model=list[SemesterBase])
def list_semesters(db: Session = Depends(get_db)):
    """
    List all semesters.
    """
    semesters = db.query(Semester).order_by(Semester.registration_start.desc()).all()
    return semesters


@router.get("/{semester_id}", response_model=SemesterDetail)
def get_semester(semester_id: UUID, db: Session = Depends(get_db)):
    """
    Get a single semester by ID.
    """
    semester = db.query(Semester).filter(Semester.id == semester_id).first()
    if not semester:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Semester not found",
        )
    return semester

