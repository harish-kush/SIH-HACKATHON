from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
from bson import ObjectId
from fastapi import HTTPException, status

from app.core.database import get_database
from app.models.student import StudentCreate, StudentUpdate, StudentInDB, Student


class StudentService:
    def __init__(self):
        self.collection_name = "students"
    
    async def get_database(self) -> AsyncIOMotorDatabase:
        return await get_database()
    
    async def create_student(self, student_create: StudentCreate) -> StudentInDB:
        """Create new student"""
        db = await self.get_database()
        
        # Check if student with scholar_id already exists
        existing_student = await db[self.collection_name].find_one({"scholar_id": student_create.scholar_id})
        if existing_student:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Student with this scholar ID already exists"
            )
        
        # Create student document
        student_dict = student_create.dict()
        student_dict["created_at"] = datetime.utcnow()
        student_dict["updated_at"] = datetime.utcnow()
        student_dict["current_risk_score"] = None
        student_dict["last_prediction_date"] = None
        
        result = await db[self.collection_name].insert_one(student_dict)
        student_dict["_id"] = str(result.inserted_id)
        
        return StudentInDB(**student_dict)
    
    async def get_student_by_id(self, student_id: str) -> Optional[StudentInDB]:
        """Get student by ID"""
        db = await self.get_database()
        try:
            student_data = await db[self.collection_name].find_one({"_id": ObjectId(student_id)})
        except:
            return None
        
        if student_data:
            student_data["_id"] = str(student_data["_id"])
            return StudentInDB(**student_data)
        return None
    
    async def get_student_by_scholar_id(self, scholar_id: str) -> Optional[StudentInDB]:
        """Get student by scholar ID"""
        db = await self.get_database()
        student_data = await db[self.collection_name].find_one({"scholar_id": scholar_id})
        
        if student_data:
            student_data["_id"] = str(student_data["_id"])
            return StudentInDB(**student_data)
        return None
    
    async def get_students(
        self, 
        skip: int = 0, 
        limit: int = 100,
        mentor_id: Optional[str] = None,
        branch: Optional[str] = None,
        year: Optional[str] = None,
        risk_threshold: Optional[float] = None
    ) -> List[StudentInDB]:
        """Get students with optional filters"""
        db = await self.get_database()
        
        # Build filter query
        filter_query = {"is_active": True}
        if mentor_id:
            filter_query["mentor_id"] = mentor_id
        if branch:
            filter_query["branch"] = branch
        if year:
            filter_query["year"] = year
        if risk_threshold:
            filter_query["current_risk_score"] = {"$gte": risk_threshold}
        
        cursor = db[self.collection_name].find(filter_query).skip(skip).limit(limit)
        students = []
        
        async for student_data in cursor:
            student_data["_id"] = str(student_data["_id"])
            students.append(StudentInDB(**student_data))
        
        return students
    
    async def update_student(self, student_id: str, student_update: StudentUpdate) -> Optional[StudentInDB]:
        """Update student"""
        db = await self.get_database()
        
        update_data = {k: v for k, v in student_update.dict().items() if v is not None}
        if not update_data:
            return await self.get_student_by_id(student_id)
        
        update_data["updated_at"] = datetime.utcnow()
        
        try:
            result = await db[self.collection_name].update_one(
                {"_id": ObjectId(student_id)},
                {"$set": update_data}
            )
            
            if result.modified_count:
                return await self.get_student_by_id(student_id)
            return None
        except:
            return None
    
    async def update_student_risk_score(self, student_id: str, risk_score: float) -> bool:
        """Update student's current risk score"""
        db = await self.get_database()
        
        try:
            result = await db[self.collection_name].update_one(
                {"_id": ObjectId(student_id)},
                {
                    "$set": {
                        "current_risk_score": risk_score,
                        "last_prediction_date": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except:
            return False
    
    async def delete_student(self, student_id: str) -> bool:
        """Soft delete student (set is_active to False)"""
        db = await self.get_database()
        
        try:
            result = await db[self.collection_name].update_one(
                {"_id": ObjectId(student_id)},
                {
                    "$set": {
                        "is_active": False,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except:
            return False
    
    async def get_students_by_mentor(self, mentor_id: str) -> List[StudentInDB]:
        """Get all students assigned to a mentor"""
        return await self.get_students(mentor_id=mentor_id)
    
    async def assign_mentor(self, student_id: str, mentor_id: str) -> bool:
        """Assign mentor to student"""
        update_data = StudentUpdate(mentor_id=mentor_id)
        result = await self.update_student(student_id, update_data)
        return result is not None


student_service = StudentService()
