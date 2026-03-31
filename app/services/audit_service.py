import uuid
import datetime
import pytz
from app.config.db import get_table
from app.config.settings import AUDIT_LOGS_TABLE
from boto3.dynamodb.conditions import Key, Attr

audit_table = get_table(AUDIT_LOGS_TABLE)

import json

def create_audit_log(performed_by_id, performed_by_name, performed_by_email, performed_by_role, 
                     task_id, task_title, action, details, 
                     task_owner_id=None, task_assigned_by_id=None,
                     priority=None, department=None, comment=None, payload=None):
    """
    Creates an audit log entry.
    """
    IST = pytz.timezone("Asia/Kolkata")
    timestamp = datetime.datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")
    log_id = str(uuid.uuid4())
    
    item = {
        "log_id": log_id,
        "performed_by_id": performed_by_id,
        "performed_by_name": performed_by_name,
        "performed_by_email": performed_by_email,
        "performed_by_role": performed_by_role,
        "task_id": task_id,
        "task_title": task_title,
        "action": action,
        "details": details,
        "timestamp": timestamp,
        "task_owner_id": task_owner_id,
        "task_assigned_by_id": task_assigned_by_id,
        "priority": priority,
        "department": department,
        "comment": comment,
        "payload": json.dumps(payload) if payload else None,
        "log_type": "GLOBAL" 
    }
    
    try:
        audit_table.put_item(Item=item)
    except Exception as e:
        print(f"Error creating audit log: {str(e)}")

def get_all_logs():
    """Admin view: all logs"""
    try:
        response = audit_table.scan()
        items = response.get("Items", [])
        items.sort(key=lambda x: x["timestamp"], reverse=True)
        return items
    except Exception as e:
        raise Exception(f"Failed to fetch all logs: {str(e)}")

def get_logs_for_coordinator(user_id):
   
    try:
        response = audit_table.scan(
            FilterExpression=Attr("task_owner_id").eq(user_id) | Attr("task_assigned_by_id").eq(user_id)
        )
        items = response.get("Items", [])
        items.sort(key=lambda x: x["timestamp"], reverse=True)
        return items
    except Exception as e:
        raise Exception(f"Failed to fetch logs for coordinator: {str(e)}")

def get_logs_for_user(user_id):
    """User view: logs of tasks assigned TO them"""
    try:
        response = audit_table.scan(
            FilterExpression=Attr("task_owner_id").eq(user_id)
        )
        items = response.get("Items", [])
        items.sort(key=lambda x: x["timestamp"], reverse=True)
        return items
    except Exception as e:
        raise Exception(f"Failed to fetch logs for user: {str(e)}")
