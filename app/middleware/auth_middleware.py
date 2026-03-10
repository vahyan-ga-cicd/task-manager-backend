from app.utils.jwt_utils import verify_token


def authenticate_user(event):
    """
    Middleware function to extract and verify user from JWT token in Lambda event
    
    Args:
        event: Lambda event object containing headers
        
    Returns:
        user_id: The authenticated user's ID
        
    Raises:
        Exception: If authentication fails
    """
    headers = event.get("headers", {})
    
    # API Gateway sometimes sends lowercase headers
    auth_header = headers.get("authorization") or headers.get("Authorization")
    
    if not auth_header:
        raise Exception("Authorization header missing")
    
    try:
        # Extract token from "Bearer <token>"
        token = auth_header.split(" ")[1]
        user_id = verify_token(token)
        return user_id
    except IndexError:
        raise Exception("Invalid authorization header format. Expected: Bearer <token>")
    except Exception as e:
        raise Exception(f"Authentication failed: {str(e)}")
