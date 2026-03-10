from fastapi import APIRouter

from app.api.v1.routes.auth_router import router as auth_router
from app.api.v1.routes.task_router import router as task_router

v1Router = APIRouter(prefix="/api/v1")

v1Router.include_router(auth_router)
v1Router.include_router(task_router)