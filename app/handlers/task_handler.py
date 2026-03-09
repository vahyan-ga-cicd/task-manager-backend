import json

from app.services.task_service import (
    create_task,
    get_tasks,
    update_task,
    delete_task
)

from app.utils.jwt_utils import verify_token
from app.utils.response import success, error


# -----------------------------
# Extract user from JWT token
# -----------------------------
def extract_user(event):

    headers = event.get("headers", {})

    # API Gateway sometimes sends lowercase headers
    auth_header = headers.get("authorization") or headers.get("Authorization")

    if not auth_header:
        raise Exception("Authorization header missing")

    token = auth_header.split(" ")[1]

    payload = verify_token(token)

    return payload["user_id"]


# -----------------------------
# Create Task
# -----------------------------
def create(event):
    try:
        user_id = extract_user(event)

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
        user_id = extract_user(event)

        tasks = get_tasks(user_id)

        return success(tasks)

    except Exception as e:
        return error(str(e))


# -----------------------------
# Update Task
# -----------------------------
def update(event):
    try:
        user_id = extract_user(event)

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
        user_id = extract_user(event)

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