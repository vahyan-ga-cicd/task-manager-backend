from boto3.dynamodb.conditions import Key

from app.config.db import get_table
from app.config.settings import USERS_TABLE, TASKS_TABLE
from app.utils.jwt_utils import generate_token

users_table = get_table(USERS_TABLE)
tasks_table = get_table(TASKS_TABLE)

from fastapi import HTTPException
from app.utils.crypto import encrypt_password,decrypt_password
def generate_id()->str:
    used_numbers = set()
    exclusive_start_key = None
    
    while True:
        scan_kwargs = {"ProjectionExpression": "user_id"}
        if exclusive_start_key:
            scan_kwargs["ExclusiveStartKey"] = exclusive_start_key
            
        response = users_table.scan(**scan_kwargs)
        items = response.get("Items", [])
        
        for item in items:
            uid = item.get("user_id", "")
            if uid.startswith("VAH"):
                try:
                    num = int(uid[3:])
                    used_numbers.add(num)
                except ValueError:
                    pass
        
        exclusive_start_key = response.get("LastEvaluatedKey")
        if not exclusive_start_key:
            break
                
    next_id = 1
    while next_id in used_numbers:
        next_id += 1
        
    return f"VAH{next_id:03d}"

def register_user(username, email, password, role="user", activation_status="active", department="IT"):

    if len(password) < 6:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 6 characters"
        )

    if len(password) > 15:
        raise HTTPException(
            status_code=400,
            detail="Password must be at most 15 characters"
        )

    user_id = generate_id()

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
            "password": encrypted_password,
            "role": role,
            "activation_status": activation_status,
            "department": department
        },
        ConditionExpression="attribute_not_exists(user_id)"
    )

    return {
       "user":{
         "user_id": user_id,
        "username": username,
        "email": email,
        "role": role,
        "activation_status": activation_status,
        "department": department
       }
    }

def login_user(email, password):

    response = users_table.query(
        IndexName="email-index",
        KeyConditionExpression=Key("email").eq(email)
    )

    items = response.get("Items", [])

  
    if not items:
        raise HTTPException(
            status_code=400,
            detail="Invalid credentials"
        )

    user = items[0]  
    
    if user.get("activation_status") == "inactive":
        raise HTTPException(
            status_code=403,
            detail="User is inactive. Contact admin."
        )

 
    decrypted_password = decrypt_password(user["password"])

    if decrypted_password != password:
        raise HTTPException(
            status_code=400,
            detail="Invalid credentials"
        )

    
    token = generate_token(user["user_id"])

    return token
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
                "email": user["email"],
                "role": user.get("role", "user"),
                "activation_status": user.get("activation_status", "active"),
                "department": user.get("department", "IT")
            }
            }
        }

    except Exception as e:
        raise Exception(f"Failed to get user: {str(e)}")