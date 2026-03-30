import uuid
import datetime
import json

from app.config.db import get_table
from app.config.redis_db import redis_client
from app.config.settings import TASKS_TABLE, ENVIRONMENT
from boto3.dynamodb.conditions import Key
from boto3.dynamodb.conditions import Attr
import datetime
import pytz

tasks_table = get_table(TASKS_TABLE)

# Global flag to disable Redis
redis_disabled = ENVIRONMENT == "development"

def create_task(user_id, title, description, priority="Normal"):
    task_id = str(uuid.uuid4())
    IST = pytz.timezone("Asia/Kolkata")
    item = {
        "user_id": user_id,
        "task_id": task_id,
        "title": title,
        "description": description,
        "status": "pending",
        "priority": priority,
        "created_at": str(datetime.datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S"))
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

def update_task_generic(user_id, task_id, updates: dict):
    if "status" in updates and updates["status"] == "ongoing":
        res = tasks_table.query(
            KeyConditionExpression=Key("user_id").eq(user_id)
        )
        existing_tasks = res.get("Items", [])
        ongoing_tasks = [t for t in existing_tasks if t.get("status") == "ongoing" and t.get("task_id") != task_id]
        if ongoing_tasks:
            raise Exception("You can only have one task as ongoing at a time.")

    set_expressions = []
    remove_expressions = []
    expression_attr_names = {}
    expression_attr_values = {}
    
    for i, (key, value) in enumerate(updates.items()):
        attr_name = f"#k{i}"
        expression_attr_names[attr_name] = key
        
        if value is None:
            remove_expressions.append(attr_name)
        else:
            attr_val = f":v{i}"
            set_expressions.append(f"{attr_name} = {attr_val}")
            expression_attr_values[attr_val] = value
            
    update_expression = ""
    if set_expressions:
        update_expression += "SET " + ", ".join(set_expressions)
    if remove_expressions:
        if update_expression:
            update_expression += " "
        update_expression += "REMOVE " + ", ".join(remove_expressions)

    tasks_table.update_item(
        Key={
            "user_id": user_id,
            "task_id": task_id
        },
        UpdateExpression=update_expression,
        ExpressionAttributeNames=expression_attr_names,
        ExpressionAttributeValues=expression_attr_values if expression_attr_values else None
    )
    
    global redis_disabled
    if not redis_disabled:
        try:
            redis_client.delete(f"tasks:{user_id}")
        except Exception as e:
            print(f"Redis error: {e}")
            redis_disabled = True

    return {"message": "task updated successfully"}

def get_task_by_id(user_id, task_id):
    """
    Fetches a specific task using partition and sort keys.
    """
    try:
        res = tasks_table.get_item(
            Key={
                "user_id": user_id,
                "task_id": task_id
            }
        )
        return res.get("Item")
    except Exception as e:
        raise Exception(f"Failed to fetch task: {str(e)}")

def update_task(
    user_id,
    task_id,
    status,
    reason=None,
    comment=None,
    completed_at=None,
    role=None,
    is_verified=False,
    updated_by=None
):

    # 🔍 Fetch task
    task = get_task_by_id(user_id, task_id)
    if not task:
        raise Exception("Task not found")

    assigned_by_id = task.get("assigned_by_id")
    task_owner_id = task.get("user_id")

    # ==================================================
    # 🔒 COORDINATOR RULES
    # ==================================================
    is_assigned_by_me = False
    is_assigned_to_me = False

    if role == "coordinator":
        is_assigned_by_me = assigned_by_id == updated_by
        is_assigned_to_me = task_owner_id == updated_by

        if not (is_assigned_by_me or is_assigned_to_me):
            raise Exception("Unauthorized task update")

        # 🎯 If task is NOT assigned to me (it's someone else's task), I can ONLY complete it
        if not is_assigned_to_me:
            if status.lower() != "complete":
                raise Exception("Coordinator can only mark task as complete")
            if not is_verified:
                raise Exception("Verification required")
            if not comment or comment.strip() == "":
                raise Exception("Comment is required for force completion")

    # ==================================================
    # ✅ UPDATE DATA
    # ==================================================
    updates = {
        "status": status
    }

    # Save coordinator metadata (ONLY when verifying someone else's task)
    if role == "coordinator" and status.lower() == "complete" and not is_assigned_to_me:
        updates["verified_by_coordinator"] = True
        updates["coordinator_comment"] = comment

    # On hold reason
    if status == "on-hold":
        updates["on_hold_reason"] = reason
    else:
        updates["on_hold_reason"] = None

    # Completion date
    if status.lower() == "complete":
        ist = pytz.timezone("Asia/Kolkata")
        if not completed_at:
            completed_at = datetime.datetime.now(ist).strftime("%Y-%m-%d")
        updates["completed_at"] = str(completed_at)
    else:
        updates["completed_at"] = None

    return update_task_generic(user_id, task_id, updates)


    

def delete_task(user_id, task_id):
    tasks_table.delete_item(
        Key={
            "user_id": user_id,
            "task_id": task_id
        }
    )
    global redis_disabled
    if not redis_disabled:
        try:
            redis_client.delete(f"tasks:{user_id}")
        except Exception as e:
            print(f"Redis error: {e}")
            redis_disabled = True
    return {"message": "task deleted successfully"}

def assign_task(assigned_to_id, assigned_to_name, assigned_to_email, assigned_by_name, assigned_by_email, title, description, deadline, priority="Normal", assigned_to_dept="IT", assigned_by_dept="IT", assigned_by_role="admin", assigned_by_id=None):
    task_id = str(uuid.uuid4())
    item = {
        "user_id": assigned_to_id,
        "task_id": task_id,
        "assigned_to_name": assigned_to_name,
        "assigned_to_email": assigned_to_email,
        "assigned_to_dept": assigned_to_dept,
        "assigned_by": assigned_by_name,
        "assigned_by_email": assigned_by_email,
        "assigned_by_dept": assigned_by_dept,
        "assigned_by_role": assigned_by_role,
        "assigned_by_id": assigned_by_id,
        "title": title,
        "description": description,
        "status": "pending",
        "priority": priority,
        "deadline": deadline,
        "created_at": str(datetime.datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S"))
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

def get_tasks_for_coordinator(user_id):
    """
    Fetch tasks assigned TO the coordinator AND tasks assigned BY the coordinator.
    """
    try:
        # 1. Tasks assigned TO the coordinator
        res_to = tasks_table.query(
            KeyConditionExpression=Key("user_id").eq(user_id)
        )
        tasks_to = res_to.get("Items", [])
        
        # 2. Tasks assigned BY the coordinator
        # Since we don't have a GSI yet, we scan with a filter. 
        # For a small app, this is acceptable.
        res_by = tasks_table.scan(
            FilterExpression=Attr("assigned_by_id").eq(user_id)
        )
        tasks_by = res_by.get("Items", [])
        
        # Combine (avoid duplicates if they assign to themselves)
        seen_ids = set()
        combined = []
        for t in tasks_to + tasks_by:
            if t["task_id"] not in seen_ids:
                combined.append(t)
                seen_ids.add(t["task_id"])
                
        return {
            "status": "success",
            "status_code": 200,
            "data": combined
        }
    except Exception as e:
        raise Exception(f"Failed to fetch tasks for coordinator {user_id}: {str(e)}")

def get_all_tasks_public(limit=10, last_key=None):
    try:
        params = {
            "Limit": limit
        }

        if last_key:
            params["ExclusiveStartKey"] = last_key

        res = tasks_table.scan(**params)

        return {
            "items": res.get("Items", []),
            "lastKey": res.get("LastEvaluatedKey")
        }

    except Exception as e:
        raise Exception(f"Failed to fetch public tasks: {str(e)}")


def get_tasks_by_admin(admin_name):
    
    try:
        response = tasks_table.scan(
            FilterExpression=Attr("assigned_by").eq(admin_name)
        )
        return response.get("Items", [])
    except Exception as e:
        raise Exception(f"Failed to fetch tasks for admin {admin_name}: {str(e)}")

# def get_task_stats(user_id):
#     try:
#         response = tasks_table.query(
#             KeyConditionExpression=Key("user_id").eq(user_id)
#         )
#         tasks = response.get("Items", [])
#         stats = {
#             "total": len(tasks),
#             "pending": len([t for t in tasks if t.get("status") == "pending"]),
#             "ongoing": len([t for t in tasks if t.get("status") == "ongoing"]),
#             "complete": len([t for t in tasks if t.get("status") == "complete"])
#         }
#         return stats
#     except Exception as e:
#         raise Exception(f"Failed to fetch stats for user {user_id}: {str(e)}")

def get_admin_task_stats(admin_name):
    
    try:
        response = tasks_table.scan(
            FilterExpression=Attr("assigned_by").eq(admin_name)
        )
        tasks = response.get("Items", [])
        stats = {
            "total": len(tasks),
            "pending": len([t for t in tasks if t.get("status") == "pending"]),
            "ongoing": len([t for t in tasks if t.get("status") == "ongoing"]),
            "complete": len([t for t in tasks if t.get("status") == "complete"]),
            "on-hold": len([t for t in tasks if t.get("status") == "on-hold"])
        }
        return stats
    except Exception as e:
        raise Exception(f"Failed to fetch stats for admin {admin_name}: {str(e)}")

def get_public_stats():
    """
    Scans all tasks to provide global statistics for the public dashboard.
    """
    try:
        # For a small app, a full scan is okay. 
        # For production with many items, this should be cached or use an aggregate table.
        response = tasks_table.scan()
        tasks = response.get("Items", [])
        
        stats = {
            "total": len(tasks),
            "pending": len([t for t in tasks if t.get("status") == "pending"]),
            "ongoing": len([t for t in tasks if t.get("status") == "ongoing"]),
            "complete": len([t for t in tasks if t.get("status") == "complete"]),
            "on-hold": len([t for t in tasks if t.get("status") == "on-hold"])
        }
        return stats
    except Exception as e:
        raise Exception(f"Failed to fetch public stats: {str(e)}")