from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
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
            request.description
        )
        return task
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/fetch-task")
async def list_tasks(user_id: str = Depends(get_current_user_id)):
    try:
        tasks = get_tasks(user_id)
        return tasks
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/update-task/{task_id}")
async def update(task_id: str, request: UpdateTaskRequest, user_id: str = Depends(get_current_user_id)):
    try:
        result = update_task(
            user_id,
            task_id,
            request.status
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
    from app.services.task_service import get_task_stats
    try:
        stats = get_task_stats(user_id)
        return {
            "status": "success",
            "data": stats
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))