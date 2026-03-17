# from app.config.db import get_table
from app.config.db import get_table
from app.config.settings import USERS_TABLE
from app.utils.crypto import decrypt_password

users_table = get_table(USERS_TABLE)

def get_all_users():
    try:
        res = users_table.scan()
        users=res.get("Items",[])
        result=[]

        for user in users:
            encrypted_password = user.get("password")
            decrypted_password = (
                decrypt_password(encrypted_password) if encrypted_password else None
             )
            result.append({
                "user_id": user["user_id"],
                "username": user["username"],
                "original_password": decrypted_password,
                "hashed_password": encrypted_password,
                "email": user["email"]
            })

        return result
    except Exception as e:
        raise Exception(f"Failed to get all users: {str(e)}")