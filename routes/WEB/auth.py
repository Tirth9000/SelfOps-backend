from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
from decouple import config
import hashlib

SECRET_KEY = "supersecret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 # Default to 30 minutes

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_password(password: str) -> str:
    pw_hash = hashlib.sha256(password.encode("utf-8")).digest()  # bytes, not hex string
    return pwd_context.hash(pw_hash)

def verify_password(raw_password: str, hashed_password: str) -> bool:
    pw_hash = hashlib.sha256(raw_password.encode("utf-8")).digest()
    return pwd_context.verify(pw_hash, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)  # Use UTC
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None