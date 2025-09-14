from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from app.api.deps import get_current_user
from app.models.user import User
from app.services.student import student_service

router = APIRouter()

class StudentManagement(BaseModel):
    id: str
    name: str
    scholar_id: str
    email: str
    phone: Optional[str] = None
    branch: str
    semester: int
    mentor_id: Optional[str] = None
    mentor_name: Optional[str] = None
    status: str
    created_at: str
    last_login: Optional[str] = None

class SystemSettings(BaseModel):
    risk_thresholds: Dict[str, float]
    alert_settings: Dict[str, Any]
    notification_settings: Dict[str, bool]
    ml_model_settings: Dict[str, Any]

class CreateStudentRequest(BaseModel):
    name: str
    scholar_id: str
    email: str
    phone: Optional[str] = None
    branch: str
    semester: int
    mentor_id: Optional[str] = None

class UpdateStudentRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    branch: Optional[str] = None
    semester: Optional[int] = None
    mentor_id: Optional[str] = None
    status: Optional[str] = None

@router.get("/students", response_model=List[StudentManagement])
async def get_all_students(
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    branch: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None)
):
    """Get all students with filtering options"""
    try:
        # Mock students data for demo
        all_students = [
            StudentManagement(
                id="STU001",
                name="John Doe",
                scholar_id="CS2021001",
                email="john.doe@student.edu",
                phone="+1234567891",
                branch="Computer Science",
                semester=6,
                mentor_id="MENTOR001",
                mentor_name="Dr. Sarah Johnson",
                status="active",
                created_at="2021-08-15T09:00:00Z",
                last_login="2024-01-14T14:30:00Z"
            ),
            StudentManagement(
                id="STU002",
                name="Jane Smith", 
                scholar_id="CS2021002",
                email="jane.smith@student.edu",
                phone="+1234567892",
                branch="Computer Science",
                semester=6,
                mentor_id="MENTOR001",
                mentor_name="Dr. Sarah Johnson",
                status="at_risk",
                created_at="2021-08-15T09:00:00Z",
                last_login="2024-01-13T10:15:00Z"
            ),
            StudentManagement(
                id="STU003",
                name="Mike Johnson",
                scholar_id="ECE2021001",
                email="mike.johnson@student.edu", 
                phone="+1234567893",
                branch="Electronics",
                semester=6,
                mentor_id="MENTOR002",
                mentor_name="Dr. Robert Wilson",
                status="excellent",
                created_at="2021-08-15T09:00:00Z",
                last_login="2024-01-15T08:45:00Z"
            ),
            StudentManagement(
                id="STU004",
                name="Emily Davis",
                scholar_id="ME2021001", 
                email="emily.davis@student.edu",
                phone="+1234567894",
                branch="Mechanical",
                semester=4,
                mentor_id="MENTOR003",
                mentor_name="Dr. Lisa Anderson",
                status="active",
                created_at="2022-08-15T09:00:00Z",
                last_login="2024-01-12T16:20:00Z"
            )
        ]
        
        # Apply filters
        filtered_students = all_students
        if branch:
            filtered_students = [s for s in filtered_students if s.branch.lower() == branch.lower()]
        if status:
            filtered_students = [s for s in filtered_students if s.status == status]
        if search:
            search_lower = search.lower()
            filtered_students = [s for s in filtered_students if 
                               search_lower in s.name.lower() or 
                               search_lower in s.scholar_id.lower() or
                               search_lower in s.email.lower()]
        
        # Apply pagination
        return filtered_students[skip:skip + limit]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get students: {str(e)}")

@router.post("/students", response_model=StudentManagement)
async def create_student(
    student_data: CreateStudentRequest,
    current_user: User = Depends(get_current_user)
):
    """Create a new student"""
    try:
        # Mock creation for demo
        new_student = StudentManagement(
            id=f"STU{len(student_data.name):03d}",
            name=student_data.name,
            scholar_id=student_data.scholar_id,
            email=student_data.email,
            phone=student_data.phone,
            branch=student_data.branch,
            semester=student_data.semester,
            mentor_id=student_data.mentor_id,
            mentor_name="Dr. Sarah Johnson" if student_data.mentor_id else None,
            status="active",
            created_at="2024-01-15T10:30:00Z",
            last_login=None
        )
        return new_student
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create student: {str(e)}")

@router.put("/students/{student_id}", response_model=StudentManagement)
async def update_student(
    student_id: str,
    student_data: UpdateStudentRequest,
    current_user: User = Depends(get_current_user)
):
    """Update student information"""
    try:
        # Mock update for demo
        updated_student = StudentManagement(
            id=student_id,
            name=student_data.name or "John Doe",
            scholar_id="CS2021001",
            email=student_data.email or "john.doe@student.edu",
            phone=student_data.phone,
            branch=student_data.branch or "Computer Science",
            semester=student_data.semester or 6,
            mentor_id=student_data.mentor_id,
            mentor_name="Dr. Sarah Johnson" if student_data.mentor_id else None,
            status=student_data.status or "active",
            created_at="2021-08-15T09:00:00Z",
            last_login="2024-01-14T14:30:00Z"
        )
        return updated_student
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update student: {str(e)}")

@router.delete("/students/{student_id}")
async def delete_student(
    student_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a student"""
    try:
        return {"message": f"Student {student_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete student: {str(e)}")

@router.get("/mentors", response_model=List[dict])
async def get_all_mentors(
    current_user: User = Depends(get_current_user)
):
    """Get all mentors for assignment"""
    try:
        mentors = [
            {
                "id": "MENTOR001",
                "name": "Dr. Sarah Johnson",
                "email": "sarah.johnson@university.edu",
                "department": "Computer Science",
                "student_count": 25,
                "specialization": "Academic Counseling"
            },
            {
                "id": "MENTOR002", 
                "name": "Dr. Robert Wilson",
                "email": "robert.wilson@university.edu",
                "department": "Electronics",
                "student_count": 22,
                "specialization": "Technical Guidance"
            },
            {
                "id": "MENTOR003",
                "name": "Dr. Lisa Anderson", 
                "email": "lisa.anderson@university.edu",
                "department": "Mechanical",
                "student_count": 18,
                "specialization": "Career Counseling"
            }
        ]
        return mentors
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get mentors: {str(e)}")

@router.get("/settings", response_model=SystemSettings)
async def get_system_settings(
    current_user: User = Depends(get_current_user)
):
    """Get current system settings"""
    try:
        settings = SystemSettings(
            risk_thresholds={
                "low_risk_max": 3.0,
                "moderate_risk_max": 6.0,
                "high_risk_min": 6.1
            },
            alert_settings={
                "auto_alert_threshold": 7.0,
                "escalation_threshold": 8.5,
                "alert_frequency_hours": 24,
                "max_alerts_per_student": 3
            },
            notification_settings={
                "email_notifications": True,
                "sms_notifications": False,
                "push_notifications": True,
                "mentor_notifications": True
            },
            ml_model_settings={
                "model_version": "v2.1",
                "prediction_frequency_days": 7,
                "feature_importance_threshold": 0.1,
                "auto_retrain": True
            }
        )
        return settings
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get settings: {str(e)}")

@router.put("/settings", response_model=SystemSettings)
async def update_system_settings(
    settings: SystemSettings,
    current_user: User = Depends(get_current_user)
):
    """Update system settings"""
    try:
        # Mock update for demo
        return settings
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update settings: {str(e)}")

@router.get("/dashboard/stats")
async def get_admin_dashboard_stats(
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive admin dashboard statistics"""
    try:
        stats = {
            "overview": {
                "total_students": 850,
                "active_students": 820,
                "at_risk_students": 85,
                "total_mentors": 45,
                "active_alerts": 23,
                "resolved_alerts_this_week": 67
            },
            "performance_metrics": {
                "overall_success_rate": 78.5,
                "avg_response_time_hours": 4.2,
                "student_satisfaction": 4.3,
                "mentor_efficiency": 87.2
            },
            "trends": {
                "student_enrollment_trend": "increasing",
                "dropout_rate_trend": "decreasing", 
                "performance_trend": "stable",
                "alert_volume_trend": "decreasing"
            },
            "branch_statistics": [
                {"branch": "Computer Science", "total": 180, "at_risk": 15, "success_rate": 82},
                {"branch": "Electronics", "total": 150, "at_risk": 12, "success_rate": 85},
                {"branch": "Mechanical", "total": 140, "at_risk": 20, "success_rate": 75},
                {"branch": "Civil", "total": 120, "at_risk": 8, "success_rate": 88},
                {"branch": "Information Technology", "total": 100, "at_risk": 10, "success_rate": 80}
            ]
        }
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard stats: {str(e)}")
