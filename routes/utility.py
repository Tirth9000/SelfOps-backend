import jwt
from datetime import datetime, timedelta
from decouple import config

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 3

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    token = jwt.encode(to_encode, config("SECRET_KEY"), algorithm=ALGORITHM)
    return token

def verify_token(token: str):
    try:
        payload = jwt.decode(token, config("SECRET_KEY"), algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None