import redis
import boto3
import os
from app.config.settings import REDIS_HOST, REDIS_PORT, ENVIRONMENT

def get_redis_host():
    if ENVIRONMENT == "production":
        try:
            ssm = boto3.client('ssm', region_name=os.getenv("AWS_REGION", "ap-south-1"))
            parameter = ssm.get_parameter(Name='/task-manager/redis-host', WithDecryption=False)
            return parameter['Parameter']['Value']
        except Exception as e:
            print(f"Failed to fetch Redis host from SSM: {e}")
            return None
    return REDIS_HOST

# Get the dynamic host
actual_redis_host = get_redis_host()

# Initialize redis_client as None initially
redis_client = None

if actual_redis_host:
    redis_client = redis.Redis(
        host=actual_redis_host,
        port=int(REDIS_PORT),
        decode_responses=True,
        socket_connect_timeout=2,
        socket_timeout=2
    )