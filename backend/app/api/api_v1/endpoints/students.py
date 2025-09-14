from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from app.models.student import Student, StudentCreate, StudentUpdate, StudentWithRisk
from app.models.user import UserInDB, UserRole
from app.services.student import student_service
from app.api.deps import get_current_active_user, get_admin_or_mentor

router = APIRouter()


@router.post("/", response_model=Student)
async def create_student(
    student_create: StudentCreate,
    current_user: UserInDB = Depends(get_admin_or_mentor)
) -> Any:
    """
    Create new student (Admin/Mentor only)
    """
    student = await student_service.create_student(student_create)
    return Student(
        id=student.id,
        name=student.name,
        scholar_id=student.scholar_id,
        email=student.email,
        parent_email=student.parent_email,
        branch=student.branch,
        year=student.year,
        phone=student.phone,
        parent_phone=student.parent_phone,
        address=student.address,
        mentor_id=student.mentor_id,
        is_active=student.is_active,
        created_at=student.created_at,
        updated_at=student.updated_at,
        current_risk_score=student.current_risk_score,
        last_prediction_date=student.last_prediction_date
    )


@router.get("/", response_model=List[Student])
async def get_students(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    branch: Optional[str] = Query(None),
    year: Optional[str] = Query(None),
    risk_threshold: Optional[float] = Query(None, ge=0, le=10),
    current_user: UserInDB = Depends(get_current_active_user)
) -> Any:
    """
    Get students with optional filters
    """
    # If user is a mentor, only show their assigned students
    mentor_filter = None
    if current_user.role == UserRole.MENTOR:
        mentor_filter = current_user.id
    
    students = await student_service.get_students(
        skip=skip,
        limit=limit,
        mentor_id=mentor_filter,
        branch=branch,
        year=year,
        risk_threshold=risk_threshold
    )
    
    return [Student(
        id=student.id,
        name=student.name,
        scholar_id=student.scholar_id,
        email=student.email,
        parent_email=student.parent_email,
        branch=student.branch,
        year=student.year,
        phone=student.phone,
        parent_phone=student.parent_phone,
        address=student.address,
        mentor_id=student.mentor_id,
        is_active=student.is_active,
        created_at=student.created_at,
        updated_at=student.updated_at,
        current_risk_score=student.current_risk_score,
        last_prediction_date=student.last_prediction_date
    ) for student in students]


@router.get("/{student_id}", response_model=Student)
async def get_student(
    student_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
) -> Any:
    """
    Get student by ID
    """
    student = await student_service.get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Check permissions: students can only view their own data, mentors can view assigned students
    if current_user.role == UserRole.STUDENT:
        # TODO: Add student user ID mapping
        pass
    elif current_user.role == UserRole.MENTOR:
        if student.mentor_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to view this student")
    
    return Student(
        id=student.id,
        name=student.name,
        scholar_id=student.scholar_id,
        email=student.email,
        parent_email=student.parent_email,
        branch=student.branch,
        year=student.year,
        phone=student.phone,
        parent_phone=student.parent_phone,
        address=student.address,
        mentor_id=student.mentor_id,
        is_active=student.is_active,
        created_at=student.created_at,
        updated_at=student.updated_at,
        current_risk_score=student.current_risk_score,
        last_prediction_date=student.last_prediction_date
    )


@router.put("/{student_id}", response_model=Student)
async def update_student(
    student_id: str,
    student_update: StudentUpdate,
    current_user: UserInDB = Depends(get_admin_or_mentor)
) -> Any:
    """
    Update student (Admin/Mentor only)
    """
    student = await student_service.update_student(student_id, student_update)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    return Student(
        id=student.id,
        name=student.name,
        scholar_id=student.scholar_id,
        email=student.email,
        parent_email=student.parent_email,
        branch=student.branch,
        year=student.year,
        phone=student.phone,
        parent_phone=student.parent_phone,
        address=student.address,
        mentor_id=student.mentor_id,
        is_active=student.is_active,
        created_at=student.created_at,
        updated_at=student.updated_at,
        current_risk_score=student.current_risk_score,
        last_prediction_date=student.last_prediction_date
    )


@router.delete("/{student_id}")
async def delete_student(
    student_id: str,
    current_user: UserInDB = Depends(get_admin_or_mentor)
) -> Any:
    """
    Delete student (Admin/Mentor only)
    """
    success = await student_service.delete_student(student_id)
    if not success:
        raise HTTPException(status_code=404, detail="Student not found")
    
    return {"message": "Student deleted successfully"}


@router.post("/{student_id}/assign-mentor")
async def assign_mentor(
    student_id: str,
    mentor_id: str,
    current_user: UserInDB = Depends(get_admin_or_mentor)
) -> Any:
    """
    Assign mentor to student
    """
    success = await student_service.assign_mentor(student_id, mentor_id)
    if not success:
        raise HTTPException(status_code=404, detail="Student not found")
    
    return {"message": "Mentor assigned successfully"}


@router.get("/mentor/{mentor_id}", response_model=List[Student])
async def get_students_by_mentor(
    mentor_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
) -> Any:
    """
    Get students assigned to a mentor
    """
    # Check permissions: mentors can only view their own students
    if current_user.role == UserRole.MENTOR and current_user.id != mentor_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    students = await student_service.get_students_by_mentor(mentor_id)
    
    return [Student(
        id=student.id,
        name=student.name,
        scholar_id=student.scholar_id,
        email=student.email,
        parent_email=student.parent_email,
        branch=student.branch,
        year=student.year,
        phone=student.phone,
        parent_phone=student.parent_phone,
        address=student.address,
        mentor_id=student.mentor_id,
        is_active=student.is_active,
        created_at=student.created_at,
        updated_at=student.updated_at,
        current_risk_score=student.current_risk_score,
        last_prediction_date=student.last_prediction_date
    ) for student in students]
