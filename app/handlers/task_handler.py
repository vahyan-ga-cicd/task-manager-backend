import json

from app.services.task_service import (
    create_task,
    get_tasks,
    update_task,
    delete_task
)

from app.middleware.auth_middleware import authenticate_user
from app.utils.response import success, error


# -----------------------------
# Create Task
# -----------------------------
def create(event):
    try:
        user_id = authenticate_user(event)

        body = event.get("body", {})

        if isinstance(body, str):
            body = json.loads(body)

        task = create_task(
            user_id,
            body["title"],
            body["description"]
        )

        return success(task)

    except Exception as e:
        return error(str(e))


# -----------------------------
# Get All Tasks for User
# -----------------------------
def list_tasks(event):
    try:
        user_id = authenticate_user(event)

        tasks = get_tasks(user_id)

        return success(tasks)

    except Exception as e:
        return error(str(e))


# -----------------------------
# Update Task
# -----------------------------
def update(event):
    try:
        user_id = authenticate_user(event)

        body = event.get("body", {})

        if isinstance(body, str):
            body = json.loads(body)

        result = update_task(
            user_id,
            body["task_id"],
            body["status"]
        )

        return success(result)

    except Exception as e:
        return error(str(e))


# -----------------------------
# Delete Task
# -----------------------------
def delete(event):
    try:
        user_id = authenticate_user(event)

        body = event.get("body", {})

        if isinstance(body, str):
            body = json.loads(body)

        result = delete_task(
            user_id,
            body["task_id"]
        )

        return success(result)

    except Exception as e:
        return error(str(e))