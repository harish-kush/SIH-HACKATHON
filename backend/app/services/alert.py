from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timedelta
from bson import ObjectId
from fastapi import HTTPException, status

from app.core.database import get_database
from app.core.config import settings
from app.models.alert import AlertCreate, AlertUpdate, AlertInDB, AlertSeverity, AlertStatus
from app.services.email import email_service
from app.services.student import student_service
from app.services.auth import auth_service


class AlertService:
    def __init__(self):
        self.collection_name = "alerts"
    
    async def get_database(self) -> AsyncIOMotorDatabase:
        return await get_database()
    
    async def create_risk_alert(
        self, 
        student_id: str, 
        risk_score: float, 
        risk_bucket: str, 
        risk_factors: List[str]
    ) -> AlertInDB:
        """Create a new risk alert"""
        db = await self.get_database()
        
        # Get student info
        student = await student_service.get_student_by_id(student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Determine severity
        if risk_bucket == "high":
            severity = AlertSeverity.HIGH
        elif risk_bucket == "moderate":
            severity = AlertSeverity.MODERATE
        else:
            severity = AlertSeverity.LOW
        
        # Create alert message
        message = f"Student {student.name} has been flagged with {risk_bucket} dropout risk (Score: {risk_score}/10)"
        
        # Set SLA deadline
        sla_deadline = datetime.utcnow() + timedelta(hours=settings.MENTOR_RESPONSE_SLA_HOURS)
        
        # Create alert
        alert_create = AlertCreate(
            student_id=student_id,
            mentor_id=student.mentor_id,
            risk_score=risk_score,
            severity=severity,
            message=message,
            shap_features=[{"feature": factor, "importance": "high"} for factor in risk_factors[:3]],
            sla_deadline=sla_deadline
        )
        
        alert_dict = alert_create.dict()
        alert_dict["created_at"] = datetime.utcnow()
        alert_dict["updated_at"] = datetime.utcnow()
        alert_dict["escalation_count"] = 0
        
        result = await db[self.collection_name].insert_one(alert_dict)
        alert_dict["_id"] = str(result.inserted_id)
        
        alert = AlertInDB(**alert_dict)
        
        # Send notifications
        await self._send_alert_notifications(alert, student)
        
        return alert
    
    async def _send_alert_notifications(self, alert: AlertInDB, student):
        """Send email notifications for alerts"""
        try:
            if alert.mentor_id and alert.severity in [AlertSeverity.HIGH, AlertSeverity.MODERATE]:
                # Get mentor info
                mentor = await auth_service.get_user_by_id(alert.mentor_id)
                if mentor:
                    risk_factors = [f["feature"] for f in alert.shap_features]
                    
                    if alert.severity == AlertSeverity.HIGH:
                        await email_service.send_high_risk_alert(
                            mentor.email,
                            student.name,
                            student.scholar_id,
                            alert.risk_score,
                            risk_factors
                        )
                    else:
                        await email_service.send_moderate_risk_notification(
                            mentor.email,
                            student.name,
                            student.scholar_id,
                            alert.risk_score
                        )
        except Exception as e:
            print(f"Error sending alert notifications: {e}")
    
    async def get_alert_by_id(self, alert_id: str) -> Optional[AlertInDB]:
        """Get alert by ID"""
        db = await self.get_database()
        try:
            alert_data = await db[self.collection_name].find_one({"_id": ObjectId(alert_id)})
        except:
            return None
        
        if alert_data:
            alert_data["_id"] = str(alert_data["_id"])
            return AlertInDB(**alert_data)
        return None
    
    async def get_alerts(
        self,
        skip: int = 0,
        limit: int = 100,
        mentor_id: Optional[str] = None,
        status: Optional[AlertStatus] = None,
        severity: Optional[AlertSeverity] = None,
        student_id: Optional[str] = None
    ) -> List[AlertInDB]:
        """Get alerts with filters"""
        db = await self.get_database()
        
        # Build filter query
        filter_query = {}
        if mentor_id:
            filter_query["mentor_id"] = mentor_id
        if status:
            filter_query["status"] = status
        if severity:
            filter_query["severity"] = severity
        if student_id:
            filter_query["student_id"] = student_id
        
        cursor = db[self.collection_name].find(filter_query).sort("created_at", -1).skip(skip).limit(limit)
        alerts = []
        
        async for alert_data in cursor:
            alert_data["_id"] = str(alert_data["_id"])
            alerts.append(AlertInDB(**alert_data))
        
        return alerts
    
    async def update_alert(self, alert_id: str, alert_update: AlertUpdate) -> Optional[AlertInDB]:
        """Update alert"""
        db = await self.get_database()
        
        update_data = {k: v for k, v in alert_update.dict().items() if v is not None}
        if not update_data:
            return await self.get_alert_by_id(alert_id)
        
        update_data["updated_at"] = datetime.utcnow()
        
        # Set timestamps for status changes
        if "status" in update_data:
            if update_data["status"] == AlertStatus.ACKNOWLEDGED:
                update_data["acknowledged_at"] = datetime.utcnow()
            elif update_data["status"] == AlertStatus.RESOLVED:
                update_data["resolved_at"] = datetime.utcnow()
        
        try:
            result = await db[self.collection_name].update_one(
                {"_id": ObjectId(alert_id)},
                {"$set": update_data}
            )
            
            if result.modified_count:
                return await self.get_alert_by_id(alert_id)
            return None
        except:
            return None
    
    async def acknowledge_alert(self, alert_id: str, mentor_id: str, notes: Optional[str] = None) -> bool:
        """Acknowledge an alert"""
        alert_update = AlertUpdate(
            status=AlertStatus.ACKNOWLEDGED,
            response_notes=notes
        )
        
        result = await self.update_alert(alert_id, alert_update)
        return result is not None
    
    async def resolve_alert(self, alert_id: str, mentor_id: str, notes: Optional[str] = None) -> bool:
        """Resolve an alert"""
        alert_update = AlertUpdate(
            status=AlertStatus.RESOLVED,
            response_notes=notes
        )
        
        result = await self.update_alert(alert_id, alert_update)
        return result is not None
    
    async def escalate_overdue_alerts(self):
        """Escalate alerts that are past SLA deadline"""
        db = await self.get_database()
        
        # Find overdue active alerts
        overdue_alerts = await self.get_alerts(
            status=AlertStatus.ACTIVE,
            limit=1000  # Process up to 1000 alerts at once
        )
        
        current_time = datetime.utcnow()
        escalated_count = 0
        
        for alert in overdue_alerts:
            if alert.sla_deadline and current_time > alert.sla_deadline:
                # Escalate alert
                await db[self.collection_name].update_one(
                    {"_id": ObjectId(alert.id)},
                    {
                        "$set": {
                            "status": AlertStatus.ESCALATED,
                            "escalation_count": alert.escalation_count + 1,
                            "updated_at": current_time
                        }
                    }
                )
                
                # Send escalation notification to admin
                await self._send_escalation_notification(alert)
                escalated_count += 1
        
        return escalated_count
    
    async def _send_escalation_notification(self, alert: AlertInDB):
        """Send escalation notification to admin"""
        try:
            # Get admin users
            db = await self.get_database()
            admin_cursor = db["users"].find({"role": "admin", "is_active": True})
            
            # Get student and mentor info
            student = await student_service.get_student_by_id(alert.student_id)
            mentor = await auth_service.get_user_by_id(alert.mentor_id) if alert.mentor_id else None
            
            if student:
                hours_overdue = int((datetime.utcnow() - alert.sla_deadline).total_seconds() / 3600)
                
                async for admin_data in admin_cursor:
                    admin_email = admin_data.get("email")
                    if admin_email:
                        await email_service.send_escalation_alert(
                            admin_email,
                            mentor.name if mentor else "Unknown",
                            student.name,
                            student.scholar_id,
                            hours_overdue
                        )
        except Exception as e:
            print(f"Error sending escalation notification: {e}")
    
    async def get_alert_stats(self, mentor_id: Optional[str] = None) -> dict:
        """Get alert statistics"""
        db = await self.get_database()
        
        filter_query = {}
        if mentor_id:
            filter_query["mentor_id"] = mentor_id
        
        # Count alerts by status
        pipeline = [
            {"$match": filter_query},
            {"$group": {
                "_id": "$status",
                "count": {"$sum": 1}
            }}
        ]
        
        status_counts = {}
        async for result in db[self.collection_name].aggregate(pipeline):
            status_counts[result["_id"]] = result["count"]
        
        # Calculate average response time for resolved alerts
        resolved_alerts = await self.get_alerts(status=AlertStatus.RESOLVED, mentor_id=mentor_id, limit=1000)
        avg_response_time = 0
        
        if resolved_alerts:
            response_times = []
            for alert in resolved_alerts:
                if alert.resolved_at and alert.created_at:
                    response_time = (alert.resolved_at - alert.created_at).total_seconds() / 3600
                    response_times.append(response_time)
            
            if response_times:
                avg_response_time = sum(response_times) / len(response_times)
        
        return {
            "total_alerts": sum(status_counts.values()),
            "active_alerts": status_counts.get("active", 0),
            "resolved_alerts": status_counts.get("resolved", 0),
            "escalated_alerts": status_counts.get("escalated", 0),
            "avg_response_time_hours": avg_response_time
        }


alert_service = AlertService()
