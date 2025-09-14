from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import connect_to_mongo, close_mongo_connection
from app.api.api_v1.api import api_router


# Lifespan for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: connect to MongoDB
    await connect_to_mongo()
    yield
    # Shutdown: close MongoDB connection
    await close_mongo_connection()


# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# ---------------------------
# CORS configuration
# ---------------------------
# Allow React frontend (http://localhost:3000)
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

# If you also have BACKEND_CORS_ORIGINS in settings, merge it
if settings.BACKEND_CORS_ORIGINS:
    origins += [str(origin) for origin in settings.BACKEND_CORS_ORIGINS]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      # allowed origins
    allow_credentials=True,
    allow_methods=["*"],        # allow all methods (GET, POST, etc.)
    allow_headers=["*"],        # allow all headers
)

# ---------------------------
# Include API routes
# ---------------------------
app.include_router(api_router, prefix=settings.API_V1_STR)

# ---------------------------
# Health check and root
# ---------------------------
@app.get("/")
async def root():
    return {"message": "Student Dropout Prediction & Counselling Platform API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "dropout-prediction-api"}
