from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.services.admin.admin_service import get_all_users, edit_user
from app.api.v1.middleware.auth_middleware import get_current_user_id
from app.services.auth_service import get_user

router = APIRouter(prefix="/admin", tags=["Admin"])

class EditUserRequest(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    activation_status: Optional[str] = None

def verify_admin(user_id: str = Depends(get_current_user_id)):
    try:
        user_info = get_user(user_id)
        role = user_info.get("data", {}).get("user_data", {}).get("role")
        if role != "admin":
            raise HTTPException(status_code=403, detail="Not authorized, admin only")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=403, detail="Not authorized")
    return user_id

@router.get("/users")
async def list_users(admin_id: str = Depends(verify_admin)):
    try:
        users = get_all_users()
        return users
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/update-user/{user_id}")
async def update_user(user_id: str, request: EditUserRequest, admin_id: str = Depends(verify_admin)):
    try:
        res = edit_user(
            user_id=user_id,
            username=request.username,
            email=request.email,
            password=request.password,
            activation_status=request.activation_status
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))