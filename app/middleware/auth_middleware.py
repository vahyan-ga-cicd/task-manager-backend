from fastapi import Header, HTTPException
from app.utils.jwt_utils import verify_token

async def get_current_user_id(authorization: str = Header(None)):
    """
    Dependency function to extract and verify user from JWT token
    
    Args:
        authorization: Authorization header containing Bearer token
        
    Returns:
        user_id: The authenticated user's ID
        
    Raises:
        HTTPException: If authentication fails
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    try:
        # Extract token from "Bearer <token>"
        token = authorization.split(" ")[1]
        user_id = verify_token(token)
        return user_id
    except IndexError:
        raise HTTPException(status_code=401, detail="Invalid authorization header format. Expected: Bearer <token>")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")
