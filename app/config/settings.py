import os
from dotenv import load_dotenv

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION")

USERS_TABLE = os.getenv("USERS_TABLE")
TASKS_TABLE = os.getenv("TASKS_TABLE")

JWT_SECRET = os.getenv("JWT_SECRET")
PASS_SECRET_KEY = os.getenv("PASS_SECRET_KEY")

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")