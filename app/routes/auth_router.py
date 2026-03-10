from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from app.services.auth_service import register_user, login_user, get_user
from app.middleware.auth_middleware import get_current_user_id

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@router.post("/register")
async def register(request: RegisterRequest):
    try:
        user = register_user(
            request.username,
            request.email,
            request.password
        )
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
async def login(request: LoginRequest):
    try:
        token = login_user(
            request.email,
            request.password
        )
        return token
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/user")
async def get_current_user(user_id: str = Depends(get_current_user_id)):
    try:
        user = get_user(user_id)
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))