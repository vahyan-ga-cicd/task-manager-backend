from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.services.task_service import (
    create_task,
    get_tasks,
    update_task,
    delete_task
)
from app.middleware.auth_middleware import get_current_user_id

router = APIRouter(prefix="/api/v1/tasks", tags=["Tasks"])

class CreateTaskRequest(BaseModel):
    title: str
    description: str

class UpdateTaskRequest(BaseModel):
    task_id: str
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

@router.put("/update-task")
async def update(request: UpdateTaskRequest, user_id: str = Depends(get_current_user_id)):
    try:
        result = update_task(
            user_id,
            request.task_id,
            request.status
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/delete-task")
async def delete(request: DeleteTaskRequest, user_id: str = Depends(get_current_user_id)):
    try:
        result = delete_task(
            user_id,
            request.task_id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))