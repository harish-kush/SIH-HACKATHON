from typing import Optional
from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timedelta

from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.database import get_database
from app.models.user import UserCreate, UserInDB, User


class AuthService:
    def __init__(self):
        self.collection_name = "users"
    
    async def get_database(self) -> AsyncIOMotorDatabase:
        return await get_database()
    
    async def authenticate_user(self, email: str, password: str) -> Optional[UserInDB]:
        """Authenticate user with email and password"""
        db = await self.get_database()
        user_data = await db[self.collection_name].find_one({"email": email})
        
        if not user_data:
            return None
        
        user = UserInDB(**user_data)
        if not verify_password(password, user.hashed_password):
            return None
        
        return user
    
    async def create_user(self, user_create: UserCreate) -> UserInDB:
        """Create new user"""
        db = await self.get_database()
        
        # Check if user already exists
        existing_user = await db[self.collection_name].find_one({"email": user_create.email})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Create user document
        user_dict = user_create.dict()
        user_dict["hashed_password"] = get_password_hash(user_create.password)
        del user_dict["password"]
        user_dict["created_at"] = datetime.utcnow()
        user_dict["updated_at"] = datetime.utcnow()
        
        result = await db[self.collection_name].insert_one(user_dict)
        user_dict["_id"] = str(result.inserted_id)
        
        return UserInDB(**user_dict)
    
    async def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        """Get user by email"""
        db = await self.get_database()
        user_data = await db[self.collection_name].find_one({"email": email})
        
        if user_data:
            user_data["_id"] = str(user_data["_id"])
            return UserInDB(**user_data)
        return None
    
    async def get_user_by_id(self, user_id: str) -> Optional[UserInDB]:
        """Get user by ID"""
        db = await self.get_database()
        user_data = await db[self.collection_name].find_one({"_id": user_id})
        
        if user_data:
            user_data["_id"] = str(user_data["_id"])
            return UserInDB(**user_data)
        return None
    
    def create_access_token_for_user(self, user: UserInDB) -> str:
        """Create access token for user"""
        return create_access_token(subject=user.id)


auth_service = AuthService()
