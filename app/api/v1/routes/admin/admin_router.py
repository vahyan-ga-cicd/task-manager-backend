from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.services.admin.admin_service import get_all_users, edit_user, create_user_by_admin, get_users_short_list
from app.api.v1.middleware.auth_middleware import get_current_user_id
from app.services.auth_service import get_user
from app.services.task_service import update_task_generic, get_all_tasks_public,assign_task,get_tasks_by_admin,get_admin_task_stats,delete_task,get_task_by_id


router = APIRouter(prefix="/admin", tags=["Admin"])

class EditUserRequest(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[str] = None
    activation_status: Optional[str] = None
    department: Optional[str] = None

class CreateUserRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    department: str = "IT"
    role: str = "user"

class AssignTaskRequest(BaseModel):
    assigned_to: str
    title: str
    description: str
    deadline: str
    priority: str = "Normal"

class AdminUpdateTaskRequest(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    on_hold_reason: Optional[str] = None

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

def verify_admin_or_coordinator(user_id: str = Depends(get_current_user_id)):
    try:
        user_info = get_user(user_id)
        user_data = user_info.get("data", {}).get("user_data", {})
        role = user_data.get("role")
        if role not in ["admin", "coordinator"]:
            raise HTTPException(status_code=403, detail="Not authorized, admin or coordinator only")
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

@router.put("/editUser/{user_id}")
async def update_user(user_id: str, request: EditUserRequest, admin_id: str = Depends(verify_admin)):
    try:
        res = edit_user(
            user_id=user_id,
            username=request.username,
            email=request.email,
            password=request.password,
            role=request.role,
            activation_status=request.activation_status,
            department=request.department
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/createuser")
async def admin_create_user(request: CreateUserRequest, admin_id: str = Depends(verify_admin)):
   
    try:
        res = create_user_by_admin(
            username=request.username,
            email=request.email,
            password=request.password,
            department=request.department,
            role=request.role
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/users-list")
async def users_short_list(admin_id: str = Depends(verify_admin_or_coordinator)):
   
    try:
        users = get_users_short_list()
        # Logic: Filter out all admins and current user from user list
        filtered_users = [u for u in users if u.get("user_id") != admin_id and u.get("role") != "admin"]
        return filtered_users
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/assign-task")
async def admin_assign_task(request: AssignTaskRequest, admin_id: str = Depends(verify_admin_or_coordinator)):
    
    try:
        # Fetch Admin's info
        admin_info = get_user(admin_id)
        admin_data = admin_info.get("data", {}).get("user_data", {})
        admin_name = admin_data.get("username", "Admin")
        admin_email = admin_data.get("email", "Admin")
        admin_dept = admin_data.get("department", "IT")
        admin_role = admin_data.get("role", "admin")
        
        # Fetch Target User's info
        user_info = get_user(request.assigned_to)
        user_data = user_info.get("data", {}).get("user_data", {})
        user_name = user_data.get("username", "Employee")
        user_email = user_data.get("email", "")
        user_dept = user_data.get("department", "IT")

        res = assign_task(
            assigned_to_id=request.assigned_to,
            assigned_to_name=user_name,
            assigned_to_email=user_email,
            assigned_by_name=admin_name,
            assigned_by_email=admin_email,
            title=request.title,
            description=request.description,
            deadline=request.deadline,
            priority=request.priority,
            assigned_to_dept=user_dept,
            assigned_by_dept=admin_dept,
            assigned_by_role=admin_role,
            assigned_by_id=admin_id
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# @router.put("/update-task/{target_user_id}/{task_id}")
# async def admin_update_task(target_user_id: str, task_id: str, request: AdminUpdateTaskRequest, admin_id: str = Depends(verify_admin_or_coordinator)):
   
#     try:
#         updates = {k: v for k, v in request.dict().items() if v is not None}
#         if not updates:
#             return {"message": "No updates provided"}

#         # Fetch admin role
#         admin_info = get_user(admin_id)
#         admin_role = admin_info.get("data", {}).get("user_data", {}).get("role")

#         # Custom logic for coordinator: cannot update status of tasks they assigned to others
#         if admin_role == "coordinator" and target_user_id != admin_id:
#             if "status" in updates:
#                  raise HTTPException(status_code=403, detail="Coordinators cannot update the status of tasks they assigned to others. They can only delete them.")

#         result = update_task_generic(target_user_id, task_id, updates)
#         return result
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))

# @router.get("/all-tasks")
# async def get_all_manageable_tasks(admin_id: str = Depends(verify_admin)):
   
#     try:
#         tasks = get_all_tasks_public()
#         return {
#             "status": "success",
#             "data": tasks
#         }
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))

@router.get("/my-tasks")
async def get_admin_own_tasks(admin_id: str = Depends(verify_admin)):
  
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
async def delete_task_by_admin(target_user_id: str, task_id: str, admin_id: str = Depends(verify_admin_or_coordinator)):

    try:
        admin_info = get_user(admin_id)
        admin_data = admin_info.get("data", {}).get("user_data", {})
        admin_role = admin_data.get("role")

        if admin_role == "coordinator":
            # Direct lookup instead of full scan
            task = get_task_by_id(target_user_id, task_id)
            
            if not task:
                raise HTTPException(status_code=404, detail="Task not found")
                
            # If the task is assigned TO the coordinator, they can't delete it
            if target_user_id == admin_id:
                raise HTTPException(status_code=403, detail="Coordinators cannot delete tasks assigned to them. They can only update the status.")
                
            # Check if they assigned it
            if task.get("assigned_by_id") != admin_id:
                raise HTTPException(status_code=403, detail="Coordinators can only delete tasks they personally assigned.")

        result = delete_task(target_user_id, task_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
