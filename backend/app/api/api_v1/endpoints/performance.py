from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import date

from app.models.performance import Performance, PerformanceCreate, PerformanceUpdate, PerformanceStats
from app.models.user import UserInDB, UserRole
from app.services.performance import performance_service
from app.api.deps import get_current_active_user, get_admin_or_mentor

router = APIRouter()


@router.post("/", response_model=Performance)
async def create_performance_record(
    performance_create: PerformanceCreate,
    current_user: UserInDB = Depends(get_admin_or_mentor)
) -> Any:
    """
    Create new performance record (Admin/Mentor only)
    """
    performance = await performance_service.create_performance_record(performance_create)
    return Performance(
        id=performance.id,
        student_id=performance.student_id,
        date=performance.date,
        attendance_percentage=performance.attendance_percentage,
        assignment_scores=performance.assignment_scores,
        semester_marks=performance.semester_marks,
        engagement_score=performance.engagement_score,
        library_hours=performance.library_hours,
        extracurricular_participation=performance.extracurricular_participation,
        disciplinary_issues=performance.disciplinary_issues,
        created_at=performance.created_at,
        updated_at=performance.updated_at
    )


@router.get("/{student_id}/history", response_model=List[Performance])
async def get_student_performance_history(
    student_id: str,
    days: int = Query(30, ge=1, le=365),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: UserInDB = Depends(get_current_active_user)
) -> Any:
    """
    Get student's performance history
    """
    # Check permissions for mentor access
    if current_user.role == UserRole.MENTOR:
        # TODO: Verify mentor is assigned to this student
        pass
    
    records = await performance_service.get_student_performance_history(
        student_id, days, skip, limit
    )
    
    return [Performance(
        id=record.id,
        student_id=record.student_id,
        date=record.date,
        attendance_percentage=record.attendance_percentage,
        assignment_scores=record.assignment_scores,
        semester_marks=record.semester_marks,
        engagement_score=record.engagement_score,
        library_hours=record.library_hours,
        extracurricular_participation=record.extracurricular_participation,
        disciplinary_issues=record.disciplinary_issues,
        created_at=record.created_at,
        updated_at=record.updated_at
    ) for record in records]


@router.get("/{student_id}/stats", response_model=PerformanceStats)
async def get_student_performance_stats(
    student_id: str,
    days: int = Query(30, ge=1, le=365),
    current_user: UserInDB = Depends(get_current_active_user)
) -> Any:
    """
    Get student's performance statistics
    """
    # Check permissions for mentor access
    if current_user.role == UserRole.MENTOR:
        # TODO: Verify mentor is assigned to this student
        pass
    
    stats = await performance_service.get_student_performance_stats(student_id, days)
    return stats


@router.put("/{performance_id}", response_model=Performance)
async def update_performance_record(
    performance_id: str,
    performance_update: PerformanceUpdate,
    current_user: UserInDB = Depends(get_admin_or_mentor)
) -> Any:
    """
    Update performance record (Admin/Mentor only)
    """
    performance = await performance_service.update_performance_record(performance_id, performance_update)
    if not performance:
        raise HTTPException(status_code=404, detail="Performance record not found")
    
    return Performance(
        id=performance.id,
        student_id=performance.student_id,
        date=performance.date,
        attendance_percentage=performance.attendance_percentage,
        assignment_scores=performance.assignment_scores,
        semester_marks=performance.semester_marks,
        engagement_score=performance.engagement_score,
        library_hours=performance.library_hours,
        extracurricular_participation=performance.extracurricular_participation,
        disciplinary_issues=performance.disciplinary_issues,
        created_at=performance.created_at,
        updated_at=performance.updated_at
    )


@router.delete("/{performance_id}")
async def delete_performance_record(
    performance_id: str,
    current_user: UserInDB = Depends(get_admin_or_mentor)
) -> Any:
    """
    Delete performance record (Admin/Mentor only)
    """
    success = await performance_service.delete_performance_record(performance_id)
    if not success:
        raise HTTPException(status_code=404, detail="Performance record not found")
    
    return {"message": "Performance record deleted successfully"}
