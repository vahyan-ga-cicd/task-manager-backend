from fastapi import APIRouter, HTTPException
from app.services.task_service import get_all_tasks_public, get_public_stats
import json
router = APIRouter(prefix="/public", tags=["Public"])


@router.get("/tasks")
async def public_tasks(limit: int = 10, last_key: str = None):
    try:
       

        parsed_key = json.loads(last_key) if last_key else None

        tasks = get_all_tasks_public(limit, parsed_key)

        return {
            "status": "success",
            "data": tasks["items"],
            "lastKey": json.dumps(tasks["lastKey"]) if tasks["lastKey"] else None
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/stats")
async def public_stats():
    try:
        stats = get_public_stats()
        return {
            "status": "success",
            "data": stats
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
