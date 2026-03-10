import bcrypt
import uuid
from boto3.dynamodb.conditions import Key

from app.config.db import get_table
from app.config.settings import USERS_TABLE, TASKS_TABLE
from app.utils.jwt_utils import generate_token

users_table = get_table(USERS_TABLE)
tasks_table = get_table(TASKS_TABLE)

from fastapi import HTTPException

def register_user(username, email, password):

    user_id = str(uuid.uuid4())

    response = users_table.query(
        IndexName="email-index",
        KeyConditionExpression=Key("email").eq(email)
    )

    items = response.get("Items", [])

    if items:
        raise HTTPException(
            status_code=400,
            detail="User with this email already exists"
        )

    password_hash = bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt()
    ).decode()

    users_table.put_item(
        Item={
            "user_id": user_id,
            "username": username,
            "email": email,
            "password_hash": password_hash
        }
    )

    return {"user_id": user_id}



def login_user(email, password):

    response = users_table.query(
        IndexName="email-index",
        KeyConditionExpression=Key("email").eq(email)
    )

    items = response.get("Items", [])

    for user in items:

        if bcrypt.checkpw(
            password.encode(),
            user["password_hash"].encode()
        ):

            token = generate_token(user["user_id"])
            return {"token": token}

    raise Exception("Invalid credentials")


def get_user(user_id):
    try:
        res = users_table.get_item(
            Key={
                "user_id": user_id
            }
        )

        user = res.get("Item")

        if not user:
            raise Exception("User not found")

        # user.pop("password_hash", None)
        res = tasks_table.query(
            KeyConditionExpression=Key("user_id").eq(user_id)
        )
        tasks = res.get("Items", [])
        tasks_count=len(tasks)
        completed_tasks=len([task for task in tasks if task["status"]=="completed"])
        pending_tasks=len([task for task in tasks if task["status"]=="pending"])
        return {
            "status": "success",
            "status_code": 200,
            "data":{
                  "task_data":{
                "tasks_count": tasks_count,
                "completed_tasks": completed_tasks,
                "pending_tasks": pending_tasks,
             },
            "user_data": {
                "user_id": user["user_id"],
                "username": user["username"],
                "email": user["email"]
            }
            }
        }

    except Exception as e:
        raise Exception(f"Failed to get user: {str(e)}")