from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class InterventionType(str, Enum):
    COUNSELING = "counseling"
    ACADEMIC_SUPPORT = "academic_support"
    PERSONAL_GUIDANCE = "personal_guidance"
    FAMILY_MEETING = "family_meeting"
    PEER_MENTORING = "peer_mentoring"
    PROFESSIONAL_REFERRAL = "professional_referral"
    OTHER = "other"


class InterventionOutcome(str, Enum):
    IMPROVED = "improved"
    STABLE = "stable"
    DECLINED = "declined"
    NO_CHANGE = "no_change"
    PENDING = "pending"


class FeedbackBase(BaseModel):
    student_id: str
    mentor_id: str
    alert_id: Optional[str] = None
    intervention_type: InterventionType
    intervention_date: datetime
    duration_minutes: Optional[int] = None
    notes: str
    outcome: InterventionOutcome = InterventionOutcome.PENDING
    follow_up_required: bool = False
    follow_up_date: Optional[datetime] = None
    student_engagement_level: int = Field(ge=1, le=5)  # 1-5 scale
    effectiveness_rating: Optional[int] = Field(None, ge=1, le=5)  # 1-5 scale


class FeedbackCreate(FeedbackBase):
    pass


class FeedbackUpdate(BaseModel):
    intervention_type: Optional[InterventionType] = None
    notes: Optional[str] = None
    outcome: Optional[InterventionOutcome] = None
    follow_up_required: Optional[bool] = None
    follow_up_date: Optional[datetime] = None
    student_engagement_level: Optional[int] = Field(None, ge=1, le=5)
    effectiveness_rating: Optional[int] = Field(None, ge=1, le=5)


class FeedbackInDB(FeedbackBase):
    id: str = Field(alias="_id")
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True


class Feedback(FeedbackBase):
    id: str = Field(alias="_id")
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True


class FeedbackStats(BaseModel):
    total_interventions: int
    avg_effectiveness_rating: float
    most_effective_intervention: InterventionType
    success_rate: float  # percentage of improved outcomes
