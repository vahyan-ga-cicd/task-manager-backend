import bcrypt
import uuid
from boto3.dynamodb.conditions import Key

from app.config.db import get_table
from app.config.settings import USERS_TABLE, TASKS_TABLE
from app.utils.jwt_utils import generate_token

users_table = get_table(USERS_TABLE)
tasks_table = get_table(TASKS_TABLE)

from fastapi import HTTPException
from app.utils.crypto import encrypt_password,decrypt_password

def register_user(username, email, password):

    user_id = str(uuid.uuid4())

    response = users_table.query(
        IndexName="email-index",
        KeyConditionExpression=Key("email").eq(email)
    )

    if response.get("Items"):
        raise HTTPException(
            status_code=400,
            detail="User already exists"
        )

    encrypted_password = encrypt_password(password)

    users_table.put_item(
        Item={
            "user_id": user_id,
            "username": username,
            "email": email,
            "password": encrypted_password   
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

        decrypted_password = decrypt_password(user["password"])

        if decrypted_password == password:
            token = generate_token(user["user_id"])
            return token

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
        completed_tasks=len([task for task in tasks if task["status"]=="complete"])
        ongoing_tasks=len([task for task in tasks if task["status"]=="ongoing"])
        pending_tasks=len([task for task in tasks if task["status"]=="pending"])
        return {
            "status": "success",
            "status_code": 200,
            "data":{
                  "task_data":{
                "tasks_count": tasks_count,
                "completed_tasks": completed_tasks,
                "ongoing_tasks":ongoing_tasks,
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