from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime, date


class PerformanceBase(BaseModel):
    student_id: str
    date: date
    attendance_percentage: float = Field(ge=0, le=100)
    assignment_scores: Dict[str, float] = {}  # subject -> score
    semester_marks: Dict[str, float] = {}  # subject -> marks
    engagement_score: float = Field(ge=0, le=10)  # 0-10 scale
    library_hours: Optional[float] = Field(ge=0, default=0)
    extracurricular_participation: Optional[int] = Field(ge=0, default=0)
    disciplinary_issues: Optional[int] = Field(ge=0, default=0)
    
    @validator('assignment_scores', 'semester_marks')
    def validate_scores(cls, v):
        for subject, score in v.items():
            if not 0 <= score <= 100:
                raise ValueError(f'Score for {subject} must be between 0 and 100')
        return v


class PerformanceCreate(PerformanceBase):
    pass


class PerformanceUpdate(BaseModel):
    attendance_percentage: Optional[float] = Field(None, ge=0, le=100)
    assignment_scores: Optional[Dict[str, float]] = None
    semester_marks: Optional[Dict[str, float]] = None
    engagement_score: Optional[float] = Field(None, ge=0, le=10)
    library_hours: Optional[float] = Field(None, ge=0)
    extracurricular_participation: Optional[int] = Field(None, ge=0)
    disciplinary_issues: Optional[int] = Field(None, ge=0)


class PerformanceInDB(PerformanceBase):
    id: str = Field(alias="_id")
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True


class Performance(PerformanceBase):
    id: str = Field(alias="_id")
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True


class PerformanceStats(BaseModel):
    avg_attendance: float
    avg_assignment_score: float
    avg_semester_marks: float
    avg_engagement: float
    total_library_hours: float
    trend_direction: str  # "improving", "declining", "stable"
