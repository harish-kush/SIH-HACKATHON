from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.models.user import User, UserCreate, Token
from app.services.auth import auth_service
from app.api.deps import get_current_active_user

router = APIRouter()


@router.post("/register", response_model=User)
async def register(user_create: UserCreate) -> Any:
    """
    Create new user account
    """
    user = await auth_service.create_user(user_create)
    return User(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at
    )


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = await auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    access_token = auth_service.create_access_token_for_user(user)
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)) -> Any:
    """
    Get current user
    """
    return current_user


@router.post("/test-token", response_model=User)
async def test_token(current_user: User = Depends(get_current_active_user)) -> Any:
    """
    Test access token
    """
    return current_user
