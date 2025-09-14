from typing import List, Optional
from pydantic import AnyHttpUrl, EmailStr, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Student Dropout Prediction Platform"
    
    # Database
    MONGODB_URI: str = "mongodb://localhost:27017/dropout_prediction"
    MONGODB_DB_NAME: str = "dropout_prediction"
    
    # JWT
    JWT_SECRET: str = "your-super-secret-jwt-key-change-this-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Email Configuration
    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_FROM: EmailStr = "noreply@dropoutprevention.com"
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_FROM_NAME: str = "Dropout Prevention System"
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # ML Configuration
    MODEL_PATH: str = "./ml/models/dropout_model.joblib"
    RETRAIN_THRESHOLD_DAYS: int = 7
    SHAP_EXPLAINER_PATH: str = "./ml/models/shap_explainer.joblib"
    
    # Alert Configuration
    MENTOR_RESPONSE_SLA_HOURS: int = 24
    HIGH_RISK_THRESHOLD: int = 7
    MODERATE_RISK_THRESHOLD: int = 4
    
    # Development
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
