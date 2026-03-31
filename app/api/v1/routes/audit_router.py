from fastapi import APIRouter, HTTPException, Depends
from app.services.audit_service import get_all_logs, get_logs_for_coordinator, get_logs_for_user
from app.api.v1.middleware.auth_middleware import get_current_user_id
from app.services.auth_service import get_user

router = APIRouter(prefix="/audit", tags=["Audit Logs"])

def verify_role(user_id: str, allowed_roles: list):
    try:
        user_info = get_user(user_id)
        role = user_info.get("data", {}).get("user_data", {}).get("role")
        if role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user_info
    except Exception as e:
        raise HTTPException(status_code=403, detail=f"Permission check failed: {str(e)}")

@router.get("/admin")
async def fetch_admin_logs(user_id: str = Depends(get_current_user_id)):
    """Admin-only view of all task audit logs."""
    verify_role(user_id, ["admin"])
    try:
        logs = get_all_logs()
        return {"status": "success", "data": logs}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/coordinator")
async def fetch_coordinator_logs(user_id: str = Depends(get_current_user_id)):
    """Coordinator-specific task logs (assigned to them and by them)."""
    verify_role(user_id, ["coordinator", "admin"])
    try:
        logs = get_logs_for_coordinator(user_id)
        return {"status": "success", "data": logs}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/user")
async def fetch_user_logs(user_id: str = Depends(get_current_user_id)):
    """User-specific task logs."""
    try:
        # Fetch role logic to potentially handle admins/coordinators here as well
        # but the request says normal user can see his own logs.
        logs = get_logs_for_user(user_id)
        return {"status": "success", "data": logs}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
