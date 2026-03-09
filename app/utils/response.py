import json

def success(data):

    return {
        "statusCode": 200,
        "body": json.dumps(data)
    }


def error(message):

    return {
        "statusCode": 400,
        "body": json.dumps({"error": message})
    }