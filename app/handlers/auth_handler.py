import json

from app.services.auth_service import register_user, login_user
from app.utils.response import success, error


def register(event):

    body = json.loads(event["body"])

    try:
        user = register_user(
            body["username"],
            body["email"],
            body["password"]
        )

        return success(user)

    except Exception as e:
        return error(str(e))


def login(event):

    body = json.loads(event["body"])

    try:
        token = login_user(
            body["email"],
            body["password"]
        )

        return success(token)

    except Exception as e:
        return error(str(e))