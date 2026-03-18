from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
import re
from app.services.auth_service import register_user, login_user, get_user
from app.api.v1.middleware.auth_middleware import get_current_user_id

router = APIRouter(prefix="/auth", tags=["Authentication"])

class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=15)
    role: Optional[str] = "user"

    @field_validator('password')
    @classmethod
    def validate_password_complexity(cls, v: str) -> str:
        if not re.search(r"[a-zA-Z]", v):
            raise ValueError("Password must contain at least one letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one number")
        if not re.search(r"[@$!%*?&_^\-+#]", v):
            raise ValueError("Password must contain at least one special character")
        return v

class LoginRequest(BaseModel):
    email: EmailStr
    password: str



# router = APIRouter()

@router.post("/register")
async def register(request: RegisterRequest):
    try:
        # Check if email already exists
        # existing_email = get_user_by_email(request.email)
        # if existing_email:
        #     raise HTTPException(
        #         status_code=400,
        #         detail="User with this email already exists"
        #     )

       

        user = register_user(
            request.username,
            request.email,
            request.password,
            request.role
        )

        return user

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/login")
async def login(request: LoginRequest):
    try:
        token = login_user(
            request.email,
            request.password
        )

        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        return {"access_token": token, "token_type": "bearer"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )
@router.get("/user")
async def get_current_user(user_id: str = Depends(get_current_user_id)):
    try:
        user = get_user(user_id)
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))