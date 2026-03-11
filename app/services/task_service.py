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