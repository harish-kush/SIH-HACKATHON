from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class AlertStatus(str, Enum):
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    ESCALATED = "escalated"


class AlertSeverity(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class AlertBase(BaseModel):
    student_id: str
    mentor_id: Optional[str] = None
    risk_score: float = Field(ge=0, le=10)
    severity: AlertSeverity
    message: str
    shap_features: Optional[List[dict]] = []  # Top contributing factors
    status: AlertStatus = AlertStatus.ACTIVE
    sla_deadline: Optional[datetime] = None


class AlertCreate(AlertBase):
    pass


class AlertUpdate(BaseModel):
    mentor_id: Optional[str] = None
    status: Optional[AlertStatus] = None
    response_notes: Optional[str] = None


class AlertInDB(AlertBase):
    id: str = Field(alias="_id")
    created_at: datetime
    updated_at: datetime
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    response_notes: Optional[str] = None
    escalation_count: int = 0

    class Config:
        populate_by_name = True


class Alert(AlertBase):
    id: str = Field(alias="_id")
    created_at: datetime
    updated_at: datetime
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    response_notes: Optional[str] = None
    escalation_count: int = 0

    class Config:
        populate_by_name = True


class AlertStats(BaseModel):
    total_alerts: int
    active_alerts: int
    resolved_alerts: int
    avg_response_time_hours: float
    escalated_alerts: int
