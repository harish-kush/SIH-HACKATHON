from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, date, timedelta
from bson import ObjectId
from fastapi import HTTPException, status
import statistics

from app.core.database import get_database
from app.models.performance import PerformanceCreate, PerformanceUpdate, PerformanceInDB, PerformanceStats


class PerformanceService:
    def __init__(self):
        self.collection_name = "performance"
    
    async def get_database(self) -> AsyncIOMotorDatabase:
        return await get_database()
    
    async def create_performance_record(self, performance_create: PerformanceCreate) -> PerformanceInDB:
        """Create new performance record"""
        db = await self.get_database()
        
        # Check if record for this student and date already exists
        existing_record = await db[self.collection_name].find_one({
            "student_id": performance_create.student_id,
            "date": performance_create.date
        })
        
        if existing_record:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Performance record for this date already exists"
            )
        
        # Create performance document
        performance_dict = performance_create.dict()
        performance_dict["created_at"] = datetime.utcnow()
        performance_dict["updated_at"] = datetime.utcnow()
        
        result = await db[self.collection_name].insert_one(performance_dict)
        performance_dict["_id"] = str(result.inserted_id)
        
        return PerformanceInDB(**performance_dict)
    
    async def get_performance_by_id(self, performance_id: str) -> Optional[PerformanceInDB]:
        """Get performance record by ID"""
        db = await self.get_database()
        try:
            performance_data = await db[self.collection_name].find_one({"_id": ObjectId(performance_id)})
        except:
            return None
        
        if performance_data:
            performance_data["_id"] = str(performance_data["_id"])
            return PerformanceInDB(**performance_data)
        return None
    
    async def get_student_performance_history(
        self, 
        student_id: str,
        days: int = 30,
        skip: int = 0,
        limit: int = 100
    ) -> List[PerformanceInDB]:
        """Get student's performance history"""
        db = await self.get_database()
        
        # Calculate date range
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        cursor = db[self.collection_name].find({
            "student_id": student_id,
            "date": {"$gte": start_date, "$lte": end_date}
        }).sort("date", -1).skip(skip).limit(limit)
        
        performance_records = []
        async for record in cursor:
            record["_id"] = str(record["_id"])
            performance_records.append(PerformanceInDB(**record))
        
        return performance_records
    
    async def update_performance_record(
        self, 
        performance_id: str, 
        performance_update: PerformanceUpdate
    ) -> Optional[PerformanceInDB]:
        """Update performance record"""
        db = await self.get_database()
        
        update_data = {k: v for k, v in performance_update.dict().items() if v is not None}
        if not update_data:
            return await self.get_performance_by_id(performance_id)
        
        update_data["updated_at"] = datetime.utcnow()
        
        try:
            result = await db[self.collection_name].update_one(
                {"_id": ObjectId(performance_id)},
                {"$set": update_data}
            )
            
            if result.modified_count:
                return await self.get_performance_by_id(performance_id)
            return None
        except:
            return None
    
    async def get_student_performance_stats(self, student_id: str, days: int = 30) -> PerformanceStats:
        """Calculate performance statistics for a student"""
        records = await self.get_student_performance_history(student_id, days)
        
        if not records:
            return PerformanceStats(
                avg_attendance=0,
                avg_assignment_score=0,
                avg_semester_marks=0,
                avg_engagement=0,
                total_library_hours=0,
                trend_direction="stable"
            )
        
        # Calculate averages
        attendance_scores = [r.attendance_percentage for r in records]
        engagement_scores = [r.engagement_score for r in records]
        library_hours = [r.library_hours or 0 for r in records]
        
        # Calculate assignment averages
        all_assignment_scores = []
        for record in records:
            if record.assignment_scores:
                all_assignment_scores.extend(record.assignment_scores.values())
        
        # Calculate semester marks averages
        all_semester_marks = []
        for record in records:
            if record.semester_marks:
                all_semester_marks.extend(record.semester_marks.values())
        
        # Determine trend direction
        trend_direction = "stable"
        if len(records) >= 2:
            recent_avg = statistics.mean([r.attendance_percentage + r.engagement_score for r in records[:len(records)//2]])
            older_avg = statistics.mean([r.attendance_percentage + r.engagement_score for r in records[len(records)//2:]])
            
            if recent_avg > older_avg * 1.05:
                trend_direction = "improving"
            elif recent_avg < older_avg * 0.95:
                trend_direction = "declining"
        
        return PerformanceStats(
            avg_attendance=statistics.mean(attendance_scores) if attendance_scores else 0,
            avg_assignment_score=statistics.mean(all_assignment_scores) if all_assignment_scores else 0,
            avg_semester_marks=statistics.mean(all_semester_marks) if all_semester_marks else 0,
            avg_engagement=statistics.mean(engagement_scores) if engagement_scores else 0,
            total_library_hours=sum(library_hours),
            trend_direction=trend_direction
        )
    
    async def get_latest_performance_features(self, student_id: str) -> Dict[str, Any]:
        """Get latest performance data formatted for ML model"""
        records = await self.get_student_performance_history(student_id, days=30)
        
        if not records:
            return {}
        
        latest_record = records[0]
        stats = await self.get_student_performance_stats(student_id, days=30)
        
        # Format features for ML model
        features = {
            "attendance_percentage": latest_record.attendance_percentage,
            "avg_assignment_score": stats.avg_assignment_score,
            "avg_semester_marks": stats.avg_semester_marks,
            "engagement_score": latest_record.engagement_score,
            "library_hours_per_week": stats.total_library_hours / 4,  # Assuming 4 weeks
            "extracurricular_participation": latest_record.extracurricular_participation or 0,
            "disciplinary_issues": latest_record.disciplinary_issues or 0,
            "trend_improving": 1 if stats.trend_direction == "improving" else 0,
            "trend_declining": 1 if stats.trend_direction == "declining" else 0
        }
        
        return features
    
    async def delete_performance_record(self, performance_id: str) -> bool:
        """Delete performance record"""
        db = await self.get_database()
        
        try:
            result = await db[self.collection_name].delete_one({"_id": ObjectId(performance_id)})
            return result.deleted_count > 0
        except:
            return False


performance_service = PerformanceService()
