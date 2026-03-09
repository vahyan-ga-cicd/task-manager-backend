from app.main import handler

event = {
 "path": "/auth/register",
 "httpMethod": "POST",
 "body": '{"email":"test@gmail.com","password":"123456"}'
}

print(handler(event, None))