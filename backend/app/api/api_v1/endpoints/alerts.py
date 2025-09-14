from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks

from app.models.alert import Alert, AlertUpdate, AlertStatus, AlertSeverity
from app.models.user import UserInDB, UserRole
from app.services.alert import alert_service
from app.api.deps import get_current_active_user, get_admin_or_mentor

router = APIRouter()


@router.get("/", response_model=List[Alert])
async def get_alerts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[AlertStatus] = Query(None),
    severity: Optional[AlertSeverity] = Query(None),
    student_id: Optional[str] = Query(None),
    current_user: UserInDB = Depends(get_current_active_user)
) -> Any:
    """
    Get alerts with optional filters
    """
    # Filter by mentor if user is a mentor
    mentor_filter = None
    if current_user.role == UserRole.MENTOR:
        mentor_filter = current_user.id
    
    alerts = await alert_service.get_alerts(
        skip=skip,
        limit=limit,
        mentor_id=mentor_filter,
        status=status,
        severity=severity,
        student_id=student_id
    )
    
    return [Alert(
        id=alert.id,
        student_id=alert.student_id,
        mentor_id=alert.mentor_id,
        risk_score=alert.risk_score,
        severity=alert.severity,
        message=alert.message,
        shap_features=alert.shap_features,
        status=alert.status,
        sla_deadline=alert.sla_deadline,
        created_at=alert.created_at,
        updated_at=alert.updated_at,
        acknowledged_at=alert.acknowledged_at,
        resolved_at=alert.resolved_at,
        response_notes=alert.response_notes,
        escalation_count=alert.escalation_count
    ) for alert in alerts]


@router.get("/{alert_id}", response_model=Alert)
async def get_alert(
    alert_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
) -> Any:
    """
    Get alert by ID
    """
    alert = await alert_service.get_alert_by_id(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    # Check permissions for mentor access
    if current_user.role == UserRole.MENTOR and alert.mentor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this alert")
    
    return Alert(
        id=alert.id,
        student_id=alert.student_id,
        mentor_id=alert.mentor_id,
        risk_score=alert.risk_score,
        severity=alert.severity,
        message=alert.message,
        shap_features=alert.shap_features,
        status=alert.status,
        sla_deadline=alert.sla_deadline,
        created_at=alert.created_at,
        updated_at=alert.updated_at,
        acknowledged_at=alert.acknowledged_at,
        resolved_at=alert.resolved_at,
        response_notes=alert.response_notes,
        escalation_count=alert.escalation_count
    )


@router.put("/{alert_id}", response_model=Alert)
async def update_alert(
    alert_id: str,
    alert_update: AlertUpdate,
    current_user: UserInDB = Depends(get_current_active_user)
) -> Any:
    """
    Update alert (Mentor/Admin only)
    """
    # Get existing alert to check permissions
    existing_alert = await alert_service.get_alert_by_id(alert_id)
    if not existing_alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    # Check permissions
    if current_user.role == UserRole.MENTOR and existing_alert.mentor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this alert")
    
    alert = await alert_service.update_alert(alert_id, alert_update)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return Alert(
        id=alert.id,
        student_id=alert.student_id,
        mentor_id=alert.mentor_id,
        risk_score=alert.risk_score,
        severity=alert.severity,
        message=alert.message,
        shap_features=alert.shap_features,
        status=alert.status,
        sla_deadline=alert.sla_deadline,
        created_at=alert.created_at,
        updated_at=alert.updated_at,
        acknowledged_at=alert.acknowledged_at,
        resolved_at=alert.resolved_at,
        response_notes=alert.response_notes,
        escalation_count=alert.escalation_count
    )


@router.post("/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str,
    notes: Optional[str] = None,
    current_user: UserInDB = Depends(get_current_active_user)
) -> Any:
    """
    Acknowledge an alert (Mentor/Admin only)
    """
    # Get existing alert to check permissions
    existing_alert = await alert_service.get_alert_by_id(alert_id)
    if not existing_alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    # Check permissions
    if current_user.role == UserRole.MENTOR and existing_alert.mentor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to acknowledge this alert")
    
    success = await alert_service.acknowledge_alert(alert_id, current_user.id, notes)
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return {"message": "Alert acknowledged successfully"}


@router.post("/{alert_id}/resolve")
async def resolve_alert(
    alert_id: str,
    notes: Optional[str] = None,
    current_user: UserInDB = Depends(get_current_active_user)
) -> Any:
    """
    Resolve an alert (Mentor/Admin only)
    """
    # Get existing alert to check permissions
    existing_alert = await alert_service.get_alert_by_id(alert_id)
    if not existing_alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    # Check permissions
    if current_user.role == UserRole.MENTOR and existing_alert.mentor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to resolve this alert")
    
    success = await alert_service.resolve_alert(alert_id, current_user.id, notes)
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return {"message": "Alert resolved successfully"}


@router.post("/escalate-overdue")
async def escalate_overdue_alerts(
    background_tasks: BackgroundTasks,
    current_user: UserInDB = Depends(get_admin_or_mentor)
) -> Any:
    """
    Manually trigger escalation of overdue alerts (Admin/Mentor only)
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can trigger escalation")
    
    background_tasks.add_task(alert_service.escalate_overdue_alerts)
    return {"message": "Escalation process initiated"}


@router.get("/stats/overview")
async def get_alert_stats(
    current_user: UserInDB = Depends(get_current_active_user)
) -> Any:
    """
    Get alert statistics
    """
    # Filter by mentor if user is a mentor
    mentor_filter = None
    if current_user.role == UserRole.MENTOR:
        mentor_filter = current_user.id
    
    stats = await alert_service.get_alert_stats(mentor_filter)
    return stats
