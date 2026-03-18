# from app.config.db import get_table
from app.config.db import get_table
from app.config.settings import USERS_TABLE
from app.utils.crypto import decrypt_password, encrypt_password

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

def edit_user(user_id: str, username: str = None, email: str = None, password: str = None):
    try:
        res = users_table.get_item(Key={"user_id": user_id})
        user = res.get("Item")
        if not user:
            raise Exception("User not found")
            
        update_expr = "SET"
        expr_attrs = {}
        expr_names = {}
        
        if username:
            update_expr += " #u = :u,"
            expr_attrs[":u"] = username
            expr_names["#u"] = "username"
        if email:
            update_expr += " #e = :e,"
            expr_attrs[":e"] = email
            expr_names["#e"] = "email"
        if password:
            enc_pass = encrypt_password(password)
            update_expr += " #p = :p,"
            expr_attrs[":p"] = enc_pass
            expr_names["#p"] = "password"
            
        if not expr_attrs:
            return {"message": "No fields to update"}
            
        update_expr = update_expr.rstrip(",")
        
        users_table.update_item(
            Key={"user_id": user_id},
            UpdateExpression=update_expr,
            ExpressionAttributeValues=expr_attrs,
            ExpressionAttributeNames=expr_names
        )
        return {"message": "User updated successfully"}
    except Exception as e:
        raise Exception(f"Failed to update user: {str(e)}")