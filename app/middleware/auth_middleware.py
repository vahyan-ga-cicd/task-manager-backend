from fastapi import Request, HTTPException
from app.utils.jwt_utils import verify_token


async def get_current_user(request: Request) -> str:
    """Extract user_id from JWT token in Authorization header"""
    
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    try:
        token = auth_header.split(" ")[1]  # Extract token from "Bearer <token>"
        user_id = verify_token(token)
        return user_id
    except IndexError:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
