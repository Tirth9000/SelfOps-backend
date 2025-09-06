from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from db.database import base, engine
from passlib.context import CryptContext
from .utility import create_access_token, verify_token
from db import models, schema
from fastapi.responses import JSONResponse
models.base.metadata.create_all(bind=engine)

router = APIRouter()

#instead of user dict connect to model DB
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

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")



@router.post('/login')
def cli_login(user_data: schema.User):
    print("Login request received")
    user = authenticate_user(user_data.username, user_data.password)
    if not user:
        return JSONResponse(content={"message": "Invalid Credentials"},
                            status_code=status.HTTP_401_UNAUTHORIZED)
    
    token = create_access_token({"sub": user_data.username})
    return JSONResponse(
        content={"message": "Login successful", 
                 "token": token},
        status_code=status.HTTP_200_OK )

    
@router.get('/protected')
def protected_route(token: dict = Depends(oauth2_scheme)):
    print("Protected route accessed")
    token_data = verify_token(token)
    if not token_data:
        return JSONResponse(content={"message": "Invalid or expired token"},
                            status_code=status.HTTP_401_UNAUTHORIZED)
    return JSONResponse(content = {"message": f"Hello {token_data['sub']}, this is a protected route"}, 
                        status_code=status.HTTP_200_OK)
