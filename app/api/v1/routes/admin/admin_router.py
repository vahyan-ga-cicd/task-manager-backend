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

class CreateUserRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str = "user"

class AssignTaskRequest(BaseModel):
    assigned_to: str
    title: str
    description: str
    deadline: str

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

@router.post("/create-user")
async def admin_create_user(request: CreateUserRequest, admin_id: str = Depends(verify_admin)):
    from app.services.admin.admin_service import create_user_by_admin
    try:
        res = create_user_by_admin(
            username=request.username,
            email=request.email,
            password=request.password,
            role=request.role
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/users-list")
async def users_short_list(admin_id: str = Depends(verify_admin)):
    from app.services.admin.admin_service import get_users_short_list
    try:
        users = get_users_short_list()
        return users
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/assign-task")
async def admin_assign_task(request: AssignTaskRequest, admin_id: str = Depends(verify_admin)):
    from app.services.task_service import assign_task
    from app.services.auth_service import get_user
    try:
        # Fetch Admin's name
        admin_info = get_user(admin_id)
        admin_name = admin_info.get("data", {}).get("user_data", {}).get("username", "Admin")
        
        # Fetch Target User's name
        user_info = get_user(request.assigned_to)
        user_name = user_info.get("data", {}).get("user_data", {}).get("username", "Employee")

        res = assign_task(
            assigned_to_id=request.assigned_to,
            assigned_to_name=user_name,
            assigned_by_name=admin_name,
            title=request.title,
            description=request.description,
            deadline=request.deadline
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/all-tasks")
async def get_all_manageable_tasks(admin_id: str = Depends(verify_admin)):
    from app.services.task_service import get_all_tasks_public
    try:
        tasks = get_all_tasks_public()
        return {
            "status": "success",
            "data": tasks
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/my-tasks")
async def get_admin_own_tasks(admin_id: str = Depends(verify_admin)):
    from app.services.task_service import get_tasks_by_admin
    from app.services.auth_service import get_user
    try:
        # Fetch Admin's name to filter by
        admin_info = get_user(admin_id)
        admin_name = admin_info.get("data", {}).get("user_data", {}).get("username", "Admin")
        
        tasks = get_tasks_by_admin(admin_name)
        return {
            "status": "success",
            "data": tasks
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/stats")
async def get_admin_stats(admin_id: str = Depends(verify_admin)):
    from app.services.task_service import get_admin_task_stats
    from app.services.auth_service import get_user
    try:
        admin_info = get_user(admin_id)
        admin_name = admin_info.get("data", {}).get("user_data", {}).get("username", "Admin")
        
        stats = get_admin_task_stats(admin_name)
        return {
            "status": "success",
            "data": stats
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/delete-task/{target_user_id}/{task_id}")
async def delete_task_by_admin(target_user_id: str, task_id: str, admin_id: str = Depends(verify_admin)):
    from app.services.task_service import delete_task
    try:
        result = delete_task(target_user_id, task_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
