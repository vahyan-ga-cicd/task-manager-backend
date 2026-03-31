import boto3
import os
from dotenv import load_dotenv

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
AUDIT_LOGS_TABLE = os.getenv("AUDIT_LOGS_TABLE", "AuditLogs")

dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
table = dynamodb.Table(AUDIT_LOGS_TABLE)

try:
    print(f"Checking table: {AUDIT_LOGS_TABLE}")
    status = table.table_status
    print(f"Status: {status}")
    
    # Try a simple put
    print("Attempting to put a test log...")
    table.put_item(Item={
        "log_id": "test-log",
        "action": "TEST_LOG",
        "timestamp": "2026-03-31 00:00:00"
    })
    print("Successfully put test log.")
    
    # Try a scan
    print("Attempting a scan...")
    items = table.scan()["Items"]
    print(f"Scan successful, found {len(items)} items.")
    
except Exception as e:
    print(f"Error: {e}")
