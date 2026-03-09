from app.handlers.auth_handler import register, login
from app.handlers.task_handler import create, list_tasks, update, delete


def handler(event, context):

    path = event["path"]
    method = event["httpMethod"]

    if path == "/auth/register" and method == "POST":
        return register(event)

    if path == "/auth/login" and method == "POST":
        return login(event)

    if path == "/tasks" and method == "POST":
        return create(event)

    if path == "/tasks" and method == "GET":
        return list_tasks(event)

    if path == "/tasks/update" and method == "PUT":
        return update(event)

    if path == "/tasks/delete" and method == "DELETE":
        return delete(event)

    return {
        "statusCode": 404,
        "body": "Not found"
    }