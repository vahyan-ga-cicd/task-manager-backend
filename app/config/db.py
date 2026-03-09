import boto3
from app.config.settings import AWS_REGION

dynamodb = boto3.resource(
    "dynamodb",
    region_name=AWS_REGION
)

def get_table(name):
    return dynamodb.Table(name)