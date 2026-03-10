from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from app.services.auth_service import register_user, login_user, get_user
from app.api.v1.middleware.auth_middleware import get_current_user_id

router = APIRouter(prefix="/auth", tags=["Authentication"])

class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

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
            request.password
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