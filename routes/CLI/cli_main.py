from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from db.database import base, engine
from passlib.context import CryptContext
from .service import *
from db import models, schema
from fastapi.responses import JSONResponse
models.base.metadata.create_all(bind=engine)

router = APIRouter()
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

    
#test
@router.get('/protected')
def protected_route(token: dict = Depends(oauth2_scheme)):
    print("Protected route accessed")
    token_data = verify_token(token)
    if not token_data:
        return JSONResponse(content={"message": "Invalid or expired token"},
                            status_code=status.HTTP_401_UNAUTHORIZED)
    return JSONResponse(content = {"message": f"Hello {token_data['sub']}, this is a protected route"}, 
                        status_code=status.HTTP_200_OK)
