from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime
from app.services.task_service import (
    create_task,
    get_tasks,
    update_task,
    delete_task
)
from app.api.v1.middleware.auth_middleware import get_current_user_id

router = APIRouter(prefix="/tasks", tags=["Tasks"])

class CreateTaskRequest(BaseModel):
    title: str
    description: str
    priority: str = "Normal"

class UpdateTaskRequest(BaseModel):
    
    status: str

class DeleteTaskRequest(BaseModel):
    task_id: str

@router.post("/create-task")
async def create(request: CreateTaskRequest, user_id: str = Depends(get_current_user_id)):
    try:
        task = create_task(
            user_id,
            request.title,
            request.description,
            request.priority
        )
        return task
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/fetch-task")
async def list_tasks(user_id: str = Depends(get_current_user_id)):
    from app.services.auth_service import get_user
    try:
        user_info = get_user(user_id)
        user_role = user_info.get("data", {}).get("user_data", {}).get("role", "user")
        
        if user_role == "coordinator":
            from app.services.task_service import get_tasks_for_coordinator
            return get_tasks_for_coordinator(user_id)
            
        tasks = get_tasks(user_id)
        return tasks
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/update-task/{task_id}")
async def update(
    task_id: str,
    request: UpdateTaskRequest,
    user_id: str = Depends(get_current_user_id)
):
    try:
        result = update_task(
            user_id=user_id,
            task_id=task_id,
            status=request.status
        )

        return result

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

        
@router.delete("/delete-task/{task_id}")
async def delete(task_id: str, user_id: str = Depends(get_current_user_id)):
    try:
        result = delete_task(
            user_id,
            task_id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/stats")
async def fetch_stats(user_id: str = Depends(get_current_user_id)):
    from app.services.task_service import get_tasks, get_tasks_for_coordinator
    from app.services.auth_service import get_user
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
            "complete": len([t for t in tasks if t.get("status") == "complete"])
        }
        return {
            "status": "success",
            "data": stats
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))