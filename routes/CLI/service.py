from db.models import User
from routes.WEB.auth import verify_password


async def authenticate_user(email: str, password: str):
    user = await User.find_one({"email": email})
    if not user or not verify_password(password, user.password):
        print(f"Authentication failed for email: {email}")
        return None
    return user
