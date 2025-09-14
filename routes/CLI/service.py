import jwt
from decouple import config



users_db = {                    
    'user1': {
        "username": "user1",
        "password": "password1"
        },
    'user2':{
        "username": "user2", 
        "password": 'password2'
        },
    }

def authenticate_user(username: str, password: str):
    user = users_db.get(username)
    if not user:
        return None
    # if not pwd_context.verify(password, user["password"]):
    if not password == user["password"]:
        return None
    return user


def create_access_token(data: dict):
    to_encode = data.copy()
    token = jwt.encode(to_encode, config("SECRET_KEY"), algorithm=config("ALGORITHM"))
    return token

def verify_token(token: str):
    try:
        payload = jwt.decode(token, config("SECRET_KEY"), algorithms=[config("ALGORITHM")])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None