import json

from app.services.auth_service import register_user, login_user, get_user
from app.utils.response import success, error
from app.middleware.auth_middleware import authenticate_user

def register(event):
    try:
        body_str = event.get("body", "{}")
        if isinstance(body_str, str):
            body = json.loads(body_str)
        else:
            body = body_str

        user = register_user(
            body["username"],
            body["email"],
            body["password"]
        )

        return success(user)

    except Exception as e:
        return error(str(e))


def login(event):
    try:
        body_str = event.get("body", "{}")
        if isinstance(body_str, str):
            body = json.loads(body_str)
        else:
            body = body_str

        token = login_user(
            body["email"],
            body["password"]
        )

        return success(token)

    except Exception as e:
        return error(str(e))


def get_current_user(event):
   
    try:
        user_id = authenticate_user(event)
        
        user = get_user(user_id)
        
        return success(user)
        
    except Exception as e:
        return error(str(e))