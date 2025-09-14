from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import openai
import os
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()

class ChatMessage(BaseModel):
    message: str
    student_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    suggestions: List[str] = []

# Mock AI responses for demo purposes
MOCK_RESPONSES = {
    "stress": "I understand you're feeling stressed. Here are some techniques that can help: 1) Take deep breaths, 2) Break tasks into smaller parts, 3) Talk to your mentor or counselor. Would you like specific study tips?",
    "study": "Great question about studying! Here are some effective study strategies: 1) Use the Pomodoro technique (25 min study, 5 min break), 2) Create a study schedule, 3) Find a quiet study space, 4) Use active recall methods. What subject are you struggling with?",
    "attendance": "I see you're concerned about attendance. Regular attendance is crucial for academic success. If you're having issues, consider: 1) Setting multiple alarms, 2) Preparing the night before, 3) Finding a study buddy, 4) Speaking with your mentor about any challenges.",
    "grades": "Let's work on improving your grades! Here are some strategies: 1) Review your past assignments to identify weak areas, 2) Attend office hours, 3) Form study groups, 4) Use online resources, 5) Practice past papers. Which subject needs the most attention?",
    "motivation": "It's normal to feel unmotivated sometimes. Try these approaches: 1) Set small, achievable goals, 2) Reward yourself for completing tasks, 3) Remember your long-term goals, 4) Connect with classmates, 5) Take care of your physical health. What's making you feel unmotivated?",
    "default": "I'm here to help you succeed academically! I can assist with study strategies, time management, stress management, and connecting you with resources. What would you like to talk about today?"
}

def get_ai_response(message: str) -> ChatResponse:
    """Generate AI response based on message content"""
    message_lower = message.lower()
    
    # Simple keyword matching for demo
    if any(word in message_lower for word in ["stress", "anxious", "worried", "overwhelmed"]):
        response = MOCK_RESPONSES["stress"]
        suggestions = ["Study techniques", "Time management", "Contact counselor"]
    elif any(word in message_lower for word in ["study", "learn", "exam", "test"]):
        response = MOCK_RESPONSES["study"]
        suggestions = ["Create study plan", "Find study group", "Practice tests"]
    elif any(word in message_lower for word in ["attendance", "absent", "miss class"]):
        response = MOCK_RESPONSES["attendance"]
        suggestions = ["Set reminders", "Talk to mentor", "Catch up on missed work"]
    elif any(word in message_lower for word in ["grade", "marks", "score", "performance"]):
        response = MOCK_RESPONSES["grades"]
        suggestions = ["Review assignments", "Get tutoring", "Study plan"]
    elif any(word in message_lower for word in ["motivation", "unmotivated", "lazy", "procrastinate"]):
        response = MOCK_RESPONSES["motivation"]
        suggestions = ["Set goals", "Find accountability partner", "Take breaks"]
    else:
        response = MOCK_RESPONSES["default"]
        suggestions = ["Study help", "Stress management", "Academic planning", "Contact mentor"]
    
    return ChatResponse(response=response, suggestions=suggestions)

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    chat_message: ChatMessage,
    current_user: User = Depends(get_current_user)
):
    """Chat with AI mentor for academic guidance"""
    try:
        # For demo purposes, using mock responses
        # In production, you would integrate with OpenAI or another AI service
        response = get_ai_response(chat_message.message)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get AI response: {str(e)}")

@router.get("/chat/history")
async def get_chat_history(
    current_user: User = Depends(get_current_user)
):
    """Get chat history for the current user"""
    # Mock chat history for demo
    return {
        "history": [
            {
                "id": "1",
                "message": "I'm feeling stressed about my upcoming exams",
                "response": "I understand you're feeling stressed. Here are some techniques that can help...",
                "timestamp": "2024-01-15T10:30:00Z",
                "user_id": current_user.id
            }
        ]
    }
