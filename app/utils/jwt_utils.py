import jwt
import datetime
from src.config.settings import JWT_SECRET

def generate_token(user_id):

    payload = {
        "user_id": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }

    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return token


def verify_token(token):

    decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    return decoded["user_id"]