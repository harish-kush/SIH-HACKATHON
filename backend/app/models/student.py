from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from enum import Enum


class Branch(str, Enum):
    CSE = "Computer Science Engineering"
    ECE = "Electronics and Communication Engineering"
    EEE = "Electrical and Electronics Engineering"
    MECH = "Mechanical Engineering"
    CIVIL = "Civil Engineering"
    IT = "Information Technology"
    OTHER = "Other"


class Year(str, Enum):
    FIRST = "1st Year"
    SECOND = "2nd Year"
    THIRD = "3rd Year"
    FOURTH = "4th Year"


class StudentBase(BaseModel):
    name: str
    scholar_id: str
    email: EmailStr
    parent_email: Optional[EmailStr] = None
    branch: Branch
    year: Year
    phone: Optional[str] = None
    parent_phone: Optional[str] = None
    address: Optional[str] = None
    mentor_id: Optional[str] = None
    is_active: bool = True


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    parent_email: Optional[EmailStr] = None
    branch: Optional[Branch] = None
    year: Optional[Year] = None
    phone: Optional[str] = None
    parent_phone: Optional[str] = None
    address: Optional[str] = None
    mentor_id: Optional[str] = None
    is_active: Optional[bool] = None


class StudentInDB(StudentBase):
    id: str = Field(alias="_id")
    created_at: datetime
    updated_at: datetime
    current_risk_score: Optional[float] = None
    last_prediction_date: Optional[datetime] = None

    class Config:
        populate_by_name = True


class Student(StudentBase):
    id: str = Field(alias="_id")
    created_at: datetime
    updated_at: datetime
    current_risk_score: Optional[float] = None
    last_prediction_date: Optional[datetime] = None

    class Config:
        populate_by_name = True


class StudentWithRisk(Student):
    risk_level: str  # "low", "moderate", "high"
    risk_factors: Optional[List[str]] = None
