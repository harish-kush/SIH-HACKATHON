from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Optional
from app.api.deps import get_current_user
from app.models.user import User
from app.services.student import student_service
from app.services.performance import performance_service

router = APIRouter()

class MentorContact(BaseModel):
    mentor_id: str
    name: str
    email: str
    phone: Optional[str] = None
    whatsapp: Optional[str] = None
    department: Optional[str] = None
    specialization: Optional[str] = None

class StudentContact(BaseModel):
    student_id: str
    mentor_contact: MentorContact

@router.get("/contact", response_model=StudentContact)
async def get_mentor_contact(
    current_user: User = Depends(get_current_user)
):
    """Get mentor contact information for the current student"""
    try:
        # Mock mentor contact for demo
        mentor_contact = MentorContact(
            mentor_id="MENTOR001",
            name="Dr. Sarah Johnson",
            email="mentor@example.com",
            phone="+1234567890",
            whatsapp="+1234567890",
            department="Computer Science",
            specialization="Academic Counseling"
        )
        
        return StudentContact(
            student_id=current_user.id,
            mentor_contact=mentor_contact
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get mentor contact: {str(e)}")

@router.get("/students", response_model=List[dict])
async def get_mentor_students(
    current_user: User = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=100)
):
    """Get all students assigned to the current mentor"""
    try:
        # Mock students data for demo
        students = [
            {
                "id": "STU001",
                "name": "John Doe",
                "scholar_id": "CS2021001",
                "email": "john.doe@student.edu",
                "phone": "+1234567891",
                "branch": "Computer Science",
                "semester": 6,
                "current_risk_score": 0.4,
                "attendance_percentage": 78.5,
                "avg_marks": 75.2,
                "last_interaction": "2024-01-10T14:30:00Z",
                "status": "active"
            },
            {
                "id": "STU002", 
                "name": "Jane Smith",
                "scholar_id": "CS2021002",
                "email": "jane.smith@student.edu",
                "phone": "+1234567892",
                "branch": "Computer Science",
                "semester": 6,
                "current_risk_score": 0.7,
                "attendance_percentage": 65.3,
                "avg_marks": 68.8,
                "last_interaction": "2024-01-08T09:15:00Z",
                "status": "at_risk"
            },
            {
                "id": "STU003",
                "name": "Mike Johnson",
                "scholar_id": "CS2021003", 
                "email": "mike.johnson@student.edu",
                "phone": "+1234567893",
                "branch": "Computer Science",
                "semester": 6,
                "current_risk_score": 0.2,
                "attendance_percentage": 92.1,
                "avg_marks": 88.5,
                "last_interaction": "2024-01-12T16:45:00Z",
                "status": "excellent"
            }
        ]
        
        return students[:limit]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get students: {str(e)}")

@router.get("/analytics", response_model=dict)
async def get_mentor_analytics(
    current_user: User = Depends(get_current_user)
):
    """Get performance analytics for mentor's students"""
    try:
        # Mock analytics data
        analytics = {
            "total_students": 25,
            "at_risk_students": 6,
            "excellent_students": 8,
            "average_students": 11,
            "overall_performance": {
                "avg_attendance": 78.4,
                "avg_marks": 74.2,
                "avg_risk_score": 0.45
            },
            "trends": {
                "attendance_trend": "improving",
                "performance_trend": "stable",
                "risk_trend": "decreasing"
            },
            "monthly_stats": [
                {"month": "Jan", "at_risk": 8, "interventions": 12, "success_rate": 75},
                {"month": "Feb", "at_risk": 7, "interventions": 10, "success_rate": 80},
                {"month": "Mar", "at_risk": 6, "interventions": 8, "success_rate": 85}
            ],
            "subject_performance": [
                {"subject": "Mathematics", "avg_score": 72.5, "at_risk_count": 3},
                {"subject": "Physics", "avg_score": 68.2, "at_risk_count": 4},
                {"subject": "Programming", "avg_score": 81.3, "at_risk_count": 2},
                {"subject": "English", "avg_score": 76.8, "at_risk_count": 1}
            ]
        }
        
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")

@router.post("/students/{student_id}/contact")
async def contact_student(
    student_id: str,
    current_user: User = Depends(get_current_user)
):
    """Log contact attempt with student"""
    try:
        # In a real implementation, this would log the contact attempt
        return {
            "message": f"Contact logged for student {student_id}",
            "timestamp": "2024-01-15T10:30:00Z",
            "mentor_id": current_user.id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to log contact: {str(e)}")
