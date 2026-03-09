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

    token = event["headers"]["Authorization"].split(" ")[1]
    return verify_token(token)


def create(event):

    user_id = extract_user(event)

    body = json.loads(event["body"])

    task = create_task(
        user_id,
        body["title"],
        body["description"]
    )

    return success(task)


def list_tasks(event):

    user_id = extract_user(event)

    tasks = get_tasks(user_id)

    return success(tasks)


def update(event):

    user_id = extract_user(event)

    body = json.loads(event["body"])

    result = update_task(
        user_id,
        body["task_id"],
        body["status"]
    )

    return success(result)



def delete(event):

    user_id = extract_user(event)

    body = json.loads(event["body"])

    result = delete_task(
        user_id,
        body["task_id"]
    )

    return success(result)