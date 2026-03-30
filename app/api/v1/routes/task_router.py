from fastapi import Query
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime
from app.services.task_service import (
    create_task,
    get_tasks,
    update_task,
    delete_task,
    get_tasks_for_coordinator
)
from app.api.v1.middleware.auth_middleware import get_current_user_id

from app.services.auth_service import get_user

router = APIRouter(prefix="/tasks", tags=["Tasks"])

class CreateTaskRequest(BaseModel):     
    title: str
    description: str
    priority: str = "Normal"

class UpdateTaskRequest(BaseModel):
    on_hold_reason: Optional[str] = None
    status: str
    comment_by_coordinator: Optional[str] = None
    is_verified: Optional[bool] = False 

class DeleteTaskRequest(BaseModel):
    task_id: str

# @router.post("/create-task")
# async def create(request: CreateTaskRequest, user_id: str = Depends(get_current_user_id)):
#     try:
#         task = create_task(
#             user_id,
#             request.title,
#             request.description,
#             request.priority
#         )
#         return task
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))

@router.get("/fetch-task")
async def list_tasks(user_id: str = Depends(get_current_user_id)):
    
    try:
        user_info = get_user(user_id)
        user_role = user_info.get("data", {}).get("user_data", {}).get("role", "user")
        
        if user_role == "coordinator":
            
            return get_tasks_for_coordinator(user_id)
            
        tasks = get_tasks(user_id)
        return tasks
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/update-task/{task_id}")
async def update(
    task_id: str,
    request: UpdateTaskRequest,
    user_id: str = Depends(get_current_user_id),  
    target_user_id: str = Query(...)              
):
    try:
       
        user_info = get_user(user_id)
        role = user_info.get("data", {}).get("user_data", {}).get("role")

       
        current_user_id = user_id       
        task_owner_id = target_user_id  

        result = update_task(
            user_id=task_owner_id,     
            task_id=task_id,
            status=request.status,
            reason=request.on_hold_reason,
            comment=request.comment_by_coordinator,
            role=role,
            is_verified=request.is_verified,
            updated_by=current_user_id  
        )

        return result

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
        
# @router.delete("/delete-task/{task_id}")
# async def delete(task_id: str, user_id: str = Depends(get_current_user_id)):
#     try:
#         result = delete_task(
#             user_id,
#             task_id
#         )
#         return result
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))

@router.get("/stats")
async def fetch_stats(user_id: str = Depends(get_current_user_id)):
    
    try:
        user_info = get_user(user_id)
        user_role = user_info.get("data", {}).get("user_data", {}).get("role", "user")
        
        if user_role == "coordinator":
            res = get_tasks_for_coordinator(user_id)
        else:
            res = get_tasks(user_id)
            
        tasks = res.get("data", [])
        stats = {
            "total": len(tasks),
            "pending": len([t for t in tasks if t.get("status") == "pending"]),
            "ongoing": len([t for t in tasks if t.get("status") == "ongoing"]),
            "complete": len([t for t in tasks if t.get("status") == "complete"]),
            "on-hold": len([t for t in tasks if t.get("status") == "on-hold"])
        }
        return {
            "status": "success",
            "data": stats
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))