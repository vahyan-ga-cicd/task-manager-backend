import json

from app.services.task_service import (
    create_task,
    get_tasks,
    update_task,
    delete_task
)

from app.utils.jwt_utils import verify_token
from app.utils.response import success, error


def extract_user(event):
    headers = event.get("headers", {})

    auth_header = headers.get("authorization") or headers.get("Authorization")

    if not auth_header:
        raise Exception("Authorization header missing")

    token = auth_header.split(" ")[1]

    payload = verify_token(token)

    return payload["user_id"]

def create(event):
    try:
        user_id = extract_user(event)

        body = json.loads(event["body"])

        task = create_task(
            user_id,
            body["title"],
            body["description"]
        )

        return success(task)
    except Exception as e:
        return error(str(e))


def list_tasks(event):
    try:
        user_id = extract_user(event)

        tasks = get_tasks(user_id)

        return success(tasks)
    except Exception as e:
        return error(str(e))


def update(event):
    try:
        user_id = extract_user(event)

        body = json.loads(event["body"])

        result = update_task(
            user_id,
            body["task_id"],
            body["status"]
        )

        return success(result)
    except Exception as e:
        return error(str(e))


def delete(event):
    try:
        user_id = extract_user(event)

        body = json.loads(event["body"])

        result = delete_task(
            user_id,
            body["task_id"]
        )

        return success(result)
    except Exception as e:
        return error(str(e))