from typing import List, Optional
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr
from app.core.config import settings


class EmailService:
    def __init__(self):
        self.conf = ConnectionConfig(
            MAIL_USERNAME=settings.MAIL_USERNAME,
            MAIL_PASSWORD=settings.MAIL_PASSWORD,
            MAIL_FROM=settings.MAIL_FROM,
            MAIL_PORT=settings.MAIL_PORT,
            MAIL_SERVER=settings.MAIL_SERVER,
            MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
            MAIL_STARTTLS=settings.MAIL_STARTTLS,
            MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True
        )
        self.fm = FastMail(self.conf)
    
    async def send_high_risk_alert(
        self,
        mentor_email: EmailStr,
        student_name: str,
        student_id: str,
        risk_score: float,
        risk_factors: List[str]
    ):
        """Send high risk alert to mentor"""
        subject = f"🚨 HIGH RISK ALERT: {student_name} (ID: {student_id})"
        
        risk_factors_html = "".join([f"<li>{factor}</li>" for factor in risk_factors])
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #dc3545, #c82333); color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                    <h1 style="margin: 0; font-size: 24px;">🚨 HIGH RISK ALERT</h1>
                    <p style="margin: 10px 0 0 0; font-size: 16px;">Immediate attention required</p>
                </div>
                
                <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                    <h2 style="color: #dc3545; margin-top: 0;">Student Details</h2>
                    <p><strong>Name:</strong> {student_name}</p>
                    <p><strong>Student ID:</strong> {student_id}</p>
                    <p><strong>Risk Score:</strong> <span style="color: #dc3545; font-weight: bold;">{risk_score:.1f}/10</span></p>
                </div>
                
                <div style="background: #fff3cd; border: 1px solid #ffeaa7; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                    <h3 style="color: #856404; margin-top: 0;">Top Risk Factors</h3>
                    <ul style="margin: 0; padding-left: 20px;">
                        {risk_factors_html}
                    </ul>
                </div>
                
                <div style="background: #d1ecf1; border: 1px solid #bee5eb; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                    <h3 style="color: #0c5460; margin-top: 0;">Action Required</h3>
                    <p>Please contact this student within <strong>24 hours</strong> to provide appropriate intervention and support.</p>
                    <p>If you cannot respond within the SLA timeframe, the alert will be escalated to administration.</p>
                </div>
                
                <div style="text-align: center; margin-top: 30px;">
                    <a href="#" style="background: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">Access Student Dashboard</a>
                </div>
                
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #dee2e6;">
                <p style="font-size: 12px; color: #6c757d; text-align: center;">
                    This is an automated alert from the Student Dropout Prevention System.<br>
                    Please do not reply to this email.
                </p>
            </div>
        </body>
        </html>
        """
        
        message = MessageSchema(
            subject=subject,
            recipients=[mentor_email],
            body=html_body,
            subtype=MessageType.html
        )
        
        await self.fm.send_message(message)
    
    async def send_moderate_risk_notification(
        self,
        mentor_email: EmailStr,
        student_name: str,
        student_id: str,
        risk_score: float
    ):
        """Send moderate risk notification to mentor"""
        subject = f"⚠️ Moderate Risk Alert: {student_name} (ID: {student_id})"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #ffc107, #e0a800); color: #212529; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                    <h1 style="margin: 0; font-size: 24px;">⚠️ Moderate Risk Alert</h1>
                    <p style="margin: 10px 0 0 0; font-size: 16px;">Student requires attention</p>
                </div>
                
                <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                    <h2 style="color: #e0a800; margin-top: 0;">Student Details</h2>
                    <p><strong>Name:</strong> {student_name}</p>
                    <p><strong>Student ID:</strong> {student_id}</p>
                    <p><strong>Risk Score:</strong> <span style="color: #e0a800; font-weight: bold;">{risk_score:.1f}/10</span></p>
                </div>
                
                <div style="background: #fff3cd; border: 1px solid #ffeaa7; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                    <h3 style="color: #856404; margin-top: 0;">Recommended Actions</h3>
                    <ul style="margin: 0; padding-left: 20px;">
                        <li>Schedule a check-in meeting with the student</li>
                        <li>Review recent academic performance</li>
                        <li>Assess any personal challenges</li>
                        <li>Provide appropriate guidance and resources</li>
                    </ul>
                </div>
                
                <div style="text-align: center; margin-top: 30px;">
                    <a href="#" style="background: #ffc107; color: #212529; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">View Student Profile</a>
                </div>
                
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #dee2e6;">
                <p style="font-size: 12px; color: #6c757d; text-align: center;">
                    This is an automated notification from the Student Dropout Prevention System.<br>
                    Please do not reply to this email.
                </p>
            </div>
        </body>
        </html>
        """
        
        message = MessageSchema(
            subject=subject,
            recipients=[mentor_email],
            body=html_body,
            subtype=MessageType.html
        )
        
        await self.fm.send_message(message)
    
    async def send_escalation_alert(
        self,
        admin_email: EmailStr,
        mentor_name: str,
        student_name: str,
        student_id: str,
        hours_overdue: int
    ):
        """Send escalation alert to admin when mentor doesn't respond within SLA"""
        subject = f"🔴 ESCALATION: Mentor SLA Breach - {student_name}"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #dc3545, #c82333); color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                    <h1 style="margin: 0; font-size: 24px;">🔴 SLA BREACH ESCALATION</h1>
                    <p style="margin: 10px 0 0 0; font-size: 16px;">Mentor response overdue</p>
                </div>
                
                <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                    <h2 style="color: #dc3545; margin-top: 0;">Escalation Details</h2>
                    <p><strong>Student:</strong> {student_name} (ID: {student_id})</p>
                    <p><strong>Assigned Mentor:</strong> {mentor_name}</p>
                    <p><strong>Hours Overdue:</strong> <span style="color: #dc3545; font-weight: bold;">{hours_overdue} hours</span></p>
                </div>
                
                <div style="background: #f8d7da; border: 1px solid #f5c6cb; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                    <h3 style="color: #721c24; margin-top: 0;">Required Actions</h3>
                    <ul style="margin: 0; padding-left: 20px;">
                        <li>Contact the assigned mentor immediately</li>
                        <li>Consider reassigning the student to another mentor</li>
                        <li>Review mentor workload and availability</li>
                        <li>Ensure student receives timely intervention</li>
                    </ul>
                </div>
                
                <div style="text-align: center; margin-top: 30px;">
                    <a href="#" style="background: #dc3545; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; margin-right: 10px;">Admin Dashboard</a>
                    <a href="#" style="background: #6c757d; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">Reassign Mentor</a>
                </div>
                
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #dee2e6;">
                <p style="font-size: 12px; color: #6c757d; text-align: center;">
                    This is an automated escalation from the Student Dropout Prevention System.<br>
                    Please do not reply to this email.
                </p>
            </div>
        </body>
        </html>
        """
        
        message = MessageSchema(
            subject=subject,
            recipients=[admin_email],
            body=html_body,
            subtype=MessageType.html
        )
        
        await self.fm.send_message(message)


email_service = EmailService()
