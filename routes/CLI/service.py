from db.models import User
from routes.WEB.auth import verify_password  # Unified

async def authenticate_user(username: str, password: str):
    user = await User.find_one({"username": username})
    if not user or user.password != password:
        return None
    return user