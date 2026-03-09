import uuid
import datetime
import json

from app.config.db import get_table
from app.config.redis_db import redis_client
from app.config.settings import TASKS_TABLE

tasks_table = get_table(TASKS_TABLE)


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

    redis_client.delete(f"tasks:{user_id}")

    return item


def get_tasks(user_id):

    cache_key = f"tasks:{user_id}"

    cached = redis_client.get(cache_key)

    if cached:
        return json.loads(cached)

    response = tasks_table.query(
        KeyConditionExpression="user_id = :uid",
        ExpressionAttributeValues={":uid": user_id}
    )

    tasks = response["Items"]

    redis_client.set(cache_key, json.dumps(tasks))

    return tasks


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

    redis_client.delete(f"tasks:{user_id}")

    return {"message": "Task updated"}

def delete_task(user_id, task_id):

    tasks_table.delete_item(
        Key={
            "user_id": user_id,
            "task_id": task_id
        }
    )

    redis_client.delete(f"tasks:{user_id}")

    return {"message": "Task deleted"}