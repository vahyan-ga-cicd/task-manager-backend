import bcrypt
import uuid

from app.config.db import get_table
from app.config.settings import USERS_TABLE
from app.utils.jwt_utils import generate_token


users_table = get_table(USERS_TABLE)


def register_user(username, email, password):

    user_id = str(uuid.uuid4())

    password_hash = bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt()
    ).decode()

    users_table.put_item(
        Item={
            "user_id": user_id,
            "username": username,
            "email": email,
            "password_hash": password_hash
        }
    )

    return {"user_id": user_id}


def login_user(email, password):

    response = users_table.scan()

    for user in response["Items"]:

        if user["email"] == email:

            if bcrypt.checkpw(
                password.encode(),
                user["password_hash"].encode()
            ):

                token = generate_token(user["user_id"])

                return {"token": token}

    raise Exception("Invalid credentials")