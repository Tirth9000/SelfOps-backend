import jwt, redis, json, secrets
from jwt import PyJWTError
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from decouple import config


# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/web/login")
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

oauth2_scheme = HTTPBearer()


pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# r_client = redis.Redis(host=config('REDIS_HOST'), port=int(config("REDIS_PORT")), db=0)
r_client = redis.Redis.from_url(config("REDIS_URL"), ssl=True)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(raw_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(raw_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=int(config('ACCESS_TOKEN_EXPIRE_MINUTES')))  # Use UTC
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config('SECRET_KEY'), algorithm=config('ALGORITHM'))
    return encoded_jwt

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=int(config('REFRESH_TOKEN_EXPIRE_DAYS')))
    to_encode.update({"exp": expire})
    refresh_token = jwt.encode(to_encode, config('REFRESH_SECRET_KEY'), algorithm=config('ALGORITHM'))
    return refresh_token

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, config('SECRET_KEY'), algorithms=[config('ALGORITHM')])
        return payload
    except jwt.PyJWTError:
        return None

def decode_refresh_token(token: str):
    try:
        payload = jwt.decode(token, config('REFRESH_SECRET_KEY'), algorithms=[config('ALGORITHM')])
        return payload
    except jwt.PyJWTError:
        return None
        
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, config('SECRET_KEY'), algorithms=[config('ALGORITHM')])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Token is invalid or expired")


def store_share_token(user_id, app_id):
    token = secrets.token_urlsafe(10)[:20]
    data = {"user_id": user_id, "app_id": app_id}
    r_client.setex(f"share:{token}", 86400, json.dumps(data))  # TTL = 24h
    return token

def get_share_data(token):
    data = r_client.get(f"share:{token}")
    if not data:
        return {"error": "Token expired or invalid"}
    return json.loads(data)