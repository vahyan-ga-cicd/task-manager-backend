import uuid
import datetime
import json

from app.config.db import get_table
from app.config.redis_db import redis_client
from app.config.settings import TASKS_TABLE, ENVIRONMENT
from boto3.dynamodb.conditions import Key
tasks_table = get_table(TASKS_TABLE)

# Global flag to disable Redis
# In development, it's disabled by default to prevent 20+ second latency.
# In production, it's enabled by default but will auto-disable if a timeout occurs.
redis_disabled = ENVIRONMENT == "development"

def create_task(user_id, title, description):

    task_id = str(uuid.uuid4())

    item = {
        "user_id": user_id,
        "task_id": task_id,
        "title": title,
        "description": description,
        "status": "pending",
        "created_at": str(datetime.datetime.utcnow())
    }

    tasks_table.put_item(Item=item)

    global redis_disabled
    if not redis_disabled:
        try:
            redis_client.delete(f"tasks:{user_id}")
        except Exception as e:
            print(f"Redis error: {e}")
            redis_disabled = True

    return item


def get_tasks(user_id):

    cache_key = f"tasks:{user_id}"

    global redis_disabled
    cached = None
    if not redis_disabled:
        try:
            cached = redis_client.get(cache_key)
        except Exception as e:
            print(f"Redis error: {e}")
            redis_disabled = True

    if cached:
        return json.loads(cached)

    response = tasks_table.query(
        KeyConditionExpression=Key("user_id").eq(user_id)
    )

    tasks = response["Items"]

    result = {
        "status": "success",
        "status_code": 200,
        "data": tasks
    }

    if not redis_disabled:
        try:
            redis_client.setex(cache_key, 300, json.dumps(result))
        except Exception as e:
            print(f"Redis error: {e}")
            redis_disabled = True

    return result


def update_task(user_id, task_id, status):

    tasks_table.update_item(
        Key={
            "user_id": user_id,
            "task_id": task_id
        },
        UpdateExpression="SET #s = :s",
        ExpressionAttributeNames={
            "#s": "status"
        },
        ExpressionAttributeValues={
            ":s": status
        }
    )
    
    response = tasks_table.get_item(
        Key={
            "user_id": user_id,
            "task_id": task_id
        }
    )
    
    title = response["Item"]["title"]
    global redis_disabled
    if not redis_disabled:
        try:
            redis_client.delete(f"tasks:{user_id}")
        except Exception as e:
            print(f"Redis error: {e}")
            redis_disabled = True

    return {"message": f"{title} updated successfully"}

def delete_task(user_id, task_id):

    tasks_table.delete_item(
        Key={
            "user_id": user_id,
            "task_id": task_id
        }
    )
    res=tasks_table.get_item(
        Key={
            "user_id": user_id,
            "task_id": task_id
        }
    )
    # title = res["Item"]["title"]

    global redis_disabled
    if not redis_disabled:
        try:
            redis_client.delete(f"tasks:{user_id}")
        except Exception as e:
            print(f"Redis error: {e}")
            redis_disabled = True

    return {"message": "  deleted successfully"}

def assign_task(assigned_to_id, assigned_to_name, assigned_by_name, title, description, deadline):
    task_id = str(uuid.uuid4())
    item = {
        "user_id": assigned_to_id,
        "task_id": task_id,
        "assigned_to_name": assigned_to_name,
        "assigned_by": assigned_by_name,
        "title": title,
        "description": description,
        "status": "pending",
        "deadline": deadline,
        "created_at": str(datetime.datetime.utcnow())
    }
    tasks_table.put_item(Item=item)
    
    global redis_disabled
    if not redis_disabled:
        try:
            redis_client.delete(f"tasks:{assigned_to_id}")
        except Exception as e:
            print(f"Redis error: {e}")
            redis_disabled = True
            
    return item

def get_all_tasks_public():
    try:
        res = tasks_table.scan()
        return res.get("Items", [])
    except Exception as e:
        raise Exception(f"Failed to fetch public tasks: {str(e)}")

def get_tasks_by_admin(admin_name):
    from boto3.dynamodb.conditions import Attr
    try:
        response = tasks_table.scan(
            FilterExpression=Attr("assigned_by").eq(admin_name)
        )
        return response.get("Items", [])
    except Exception as e:
        raise Exception(f"Failed to fetch tasks for admin {admin_name}: {str(e)}")

def get_task_stats(user_id):
    try:
        response = tasks_table.query(
            KeyConditionExpression=Key("user_id").eq(user_id)
        )
        tasks = response.get("Items", [])
        stats = {
            "total": len(tasks),
            "pending": len([t for t in tasks if t.get("status") == "pending"]),
            "ongoing": len([t for t in tasks if t.get("status") == "ongoing"]),
            "complete": len([t for t in tasks if t.get("status") == "complete"])
        }
        return stats
    except Exception as e:
        raise Exception(f"Failed to fetch stats for user {user_id}: {str(e)}")

def get_admin_task_stats(admin_name):
    from boto3.dynamodb.conditions import Attr
    try:
        response = tasks_table.scan(
            FilterExpression=Attr("assigned_by").eq(admin_name)
        )
        tasks = response.get("Items", [])
        stats = {
            "total": len(tasks),
            "pending": len([t for t in tasks if t.get("status") == "pending"]),
            "ongoing": len([t for t in tasks if t.get("status") == "ongoing"]),
            "complete": len([t for t in tasks if t.get("status") == "complete"])
        }
        return stats
    except Exception as e:
        raise Exception(f"Failed to fetch stats for admin {admin_name}: {str(e)}")