from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class ShapFeature(BaseModel):
    feature_name: str
    feature_value: Any
    shap_value: float
    contribution: str  # "positive" or "negative"


class PredictionBase(BaseModel):
    student_id: str
    risk_score_0_1: float = Field(ge=0, le=1)  # Raw probability
    risk_score_1_10: int = Field(ge=1, le=10)  # Scaled score
    risk_bucket: str  # "low", "moderate", "high"
    model_version: str
    features_used: Dict[str, Any]
    shap_features: List[ShapFeature]
    confidence_score: float = Field(ge=0, le=1)


class PredictionCreate(PredictionBase):
    pass


class PredictionInDB(PredictionBase):
    id: str = Field(alias="_id")
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True


class Prediction(PredictionBase):
    id: str = Field(alias="_id")
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True


class PredictionResponse(BaseModel):
    student_id: str
    risk_score_0_1: float
    risk_score_1_10: int
    risk_bucket: str
    top_risk_factors: List[ShapFeature]
    recommendations: List[str]
    confidence_score: float
    prediction_date: datetime


class TimelinePoint(BaseModel):
    date: datetime
    risk_score: float
    major_events: Optional[List[str]] = []


class StudentTimeline(BaseModel):
    student_id: str
    timeline: List[TimelinePoint]
    trend: str  # "improving", "declining", "stable"
    avg_risk_score: float
