from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

from app.core.config import settings
from app.core.security import verify_token
from app.services.auth import auth_service
from app.models.user import UserInDB, UserRole

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UserInDB:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            credentials.credentials, 
            settings.JWT_SECRET, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await auth_service.get_user_by_id(user_id)
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(
    current_user: UserInDB = Depends(get_current_user)
) -> UserInDB:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_current_user_with_role(required_role: UserRole):
    """Create dependency that checks for specific user role"""
    async def role_checker(
        current_user: UserInDB = Depends(get_current_active_user)
    ) -> UserInDB:
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user
    return role_checker


def get_current_user_with_roles(required_roles: list[UserRole]):
    """Create dependency that checks for multiple allowed roles"""
    async def roles_checker(
        current_user: UserInDB = Depends(get_current_active_user)
    ) -> UserInDB:
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user
    return roles_checker


# Role-specific dependencies
get_admin_user = get_current_user_with_role(UserRole.ADMIN)
get_mentor_user = get_current_user_with_role(UserRole.MENTOR)
get_student_user = get_current_user_with_role(UserRole.STUDENT)

# Multi-role dependencies
get_admin_or_mentor = get_current_user_with_roles([UserRole.ADMIN, UserRole.MENTOR])
get_any_authenticated_user = get_current_active_user
