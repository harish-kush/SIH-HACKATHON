from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from app.models.prediction import PredictionResponse, StudentTimeline
from app.models.user import UserInDB, UserRole
from app.services.ml_prediction import ml_prediction_service
from app.services.student import student_service
from app.services.alert import alert_service
from app.api.deps import get_current_active_user, get_admin_or_mentor

router = APIRouter()


@router.get("/{student_id}", response_model=PredictionResponse)
async def predict_student_dropout_risk(
    student_id: str,
    background_tasks: BackgroundTasks,
    current_user: UserInDB = Depends(get_current_active_user)
) -> Any:
    """
    Get dropout risk prediction for a student
    """
    # Check permissions for mentor access
    if current_user.role == UserRole.MENTOR:
        student = await student_service.get_student_by_id(student_id)
        if not student or student.mentor_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to view this student")
    
    # Get prediction
    prediction = await ml_prediction_service.predict_dropout_risk(student_id)
    if not prediction:
        raise HTTPException(status_code=404, detail="Unable to generate prediction for this student")
    
    # Update student's risk score
    await student_service.update_student_risk_score(student_id, prediction.risk_score_0_1)
    
    # Create alert if high or moderate risk
    if prediction.risk_bucket in ["high", "moderate"]:
        background_tasks.add_task(
            alert_service.create_risk_alert,
            student_id,
            prediction.risk_score_1_10,
            prediction.risk_bucket,
            [f.feature_name for f in prediction.top_risk_factors]
        )
    
    return prediction


@router.get("/{student_id}/timeline", response_model=StudentTimeline)
async def get_student_risk_timeline(
    student_id: str,
    days: int = 30,
    current_user: UserInDB = Depends(get_current_active_user)
) -> Any:
    """
    Get 30-day risk timeline for a student
    """
    # Check permissions for mentor access
    if current_user.role == UserRole.MENTOR:
        student = await student_service.get_student_by_id(student_id)
        if not student or student.mentor_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to view this student")
    
    # TODO: Implement timeline service
    # For now, return mock data
    from datetime import datetime, timedelta
    from app.models.prediction import TimelinePoint
    
    timeline_points = []
    for i in range(days):
        date = datetime.utcnow() - timedelta(days=i)
        # Mock risk score - in real implementation, get from prediction history
        risk_score = 5.0 + (i % 3) - 1  # Varies between 4-7
        timeline_points.append(TimelinePoint(
            date=date,
            risk_score=risk_score,
            major_events=[]
        ))
    
    timeline_points.reverse()  # Chronological order
    
    avg_risk = sum(p.risk_score for p in timeline_points) / len(timeline_points)
    
    # Determine trend
    recent_avg = sum(p.risk_score for p in timeline_points[-7:]) / 7
    older_avg = sum(p.risk_score for p in timeline_points[:7]) / 7
    
    if recent_avg > older_avg * 1.1:
        trend = "declining"  # Risk increasing = performance declining
    elif recent_avg < older_avg * 0.9:
        trend = "improving"  # Risk decreasing = performance improving
    else:
        trend = "stable"
    
    return StudentTimeline(
        student_id=student_id,
        timeline=timeline_points,
        trend=trend,
        avg_risk_score=avg_risk
    )


@router.post("/train")
async def train_model(
    current_user: UserInDB = Depends(get_admin_or_mentor)
) -> Any:
    """
    Trigger model training (Admin/Mentor only)
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can trigger model training")
    
    # TODO: Implement background training task
    # For now, return success message
    return {"message": "Model training initiated. This may take several minutes to complete."}


@router.get("/batch/{mentor_id}")
async def get_batch_predictions(
    mentor_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
) -> Any:
    """
    Get predictions for all students assigned to a mentor
    """
    # Check permissions
    if current_user.role == UserRole.MENTOR and current_user.id != mentor_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Get mentor's students
    students = await student_service.get_students_by_mentor(mentor_id)
    
    predictions = []
    for student in students:
        try:
            prediction = await ml_prediction_service.predict_dropout_risk(student.id)
            if prediction:
                predictions.append(prediction)
        except Exception as e:
            print(f"Error predicting for student {student.id}: {e}")
            continue
    
    return predictions
