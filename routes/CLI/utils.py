from db.models import User
from backend.routes.WEB.utils import verify_password
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt import PyJWTError
from decouple import config

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/cli/login") 


async def authenticate_user(email: str, password: str):
    user = await User.find_one({"email": email})
    if not user or not verify_password(password, user.password):
        print(f"Authentication failed for email: {email}")
        return None
    return user


def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, config('SECRET_KEY'), algorithms=[config('ALGORITHM')])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Token is invalid or expired")


def cli_create_access_token(data: dict):
    return jwt.encode(data, config('SECRET_KEY'), algorithm=config('ALGORITHM'))