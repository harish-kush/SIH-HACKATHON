from fastapi import APIRouter

from app.api.api_v1.endpoints import auth, students, performance, predictions, alerts, chatbot, mentors, admin

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(students.router, prefix="/students", tags=["students"])
api_router.include_router(performance.router, prefix="/performance", tags=["performance"])
api_router.include_router(predictions.router, prefix="/predict", tags=["predictions"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(chatbot.router, prefix="/chatbot", tags=["chatbot"])
api_router.include_router(mentors.router, prefix="/mentors", tags=["mentors"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
