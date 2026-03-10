from app.handlers.auth_handler import register, login, get_current_user
from app.handlers.task_handler import create, list_tasks, update, delete
import json

def handler(event, context):
    print(event)

    path = event.get("rawPath", "")
    method = event.get("requestContext", {}).get("http", {}).get("method", "")

    # Root health check
    if path == "/" and method == "GET":
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "Task Manager API running"})
        }

    # Auth routes
    if "/auth/register" in path and method == "POST":
        return register(event)

    if "/auth/login" in path and method == "POST":
        return login(event)
    
    if "/auth/user" in path and method == "GET":
        return get_current_user(event)

    # Task routes
    if "/tasks/create-task" in path and method == "POST":
        return create(event)

    if "/tasks/fetch-task" in path and method == "GET":
        return list_tasks(event)

    if "/tasks/update-task" in path and method == "PUT":
        return update(event)

    if "/tasks/delete-task" in path and method == "DELETE":
        return delete(event)

    # Default route
    return {
        "statusCode": 404,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({
            "message": "Route not found",
            "path": path,
            "method": method
        })
    }