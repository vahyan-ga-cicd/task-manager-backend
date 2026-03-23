from fastapi import APIRouter, HTTPException
from app.services.task_service import get_all_tasks_public

router = APIRouter(prefix="/public", tags=["Public"])

@router.get("/tasks")
async def public_tasks():
    try:
        tasks = get_all_tasks_public()
        return {
            "status": "success",
            "data": tasks
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
