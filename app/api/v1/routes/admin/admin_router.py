import fastapi
from fastapi import APIRouter, HTTPException, Depends
from app.services.admin.admin_service import get_all_users

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/users")
async def list_users():
    try:
        users = get_all_users()
        return users
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))