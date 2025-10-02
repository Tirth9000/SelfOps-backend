from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from db.models import User
from routes.WEB.auth import create_access_token, decode_access_token
from pydantic import BaseModel

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/cli/login")

class LoginRequest(BaseModel):
    email: str
    password: str

async def authenticate_user(email: str, password: str):
    user = await User.find_one({"email": email})
    if not user or not user.verify_password(password):
        print(f"Authentication failed for email: {email}")
        return None
    return user

@router.post("/login")
async def cli_login(user_data: LoginRequest):
    user = await authenticate_user(user_data.email, user_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"sub": str(user.id)})
    return {
        "status": status.HTTP_200_OK,
        "message": "Login successful",
        "access_token": token,
        "token_type": "bearer"
    }

@router.get('/protected')
async def protected_route(token: str = Depends(oauth2_scheme)):
    print("Protected route accessed")
    token_data = decode_access_token(token)
    if not token_data:
        return JSONResponse(content={"message": "Invalid or expired token"},
                            status_code=status.HTTP_401_UNAUTHORIZED)
    
    user_id = token_data.get("sub")
    user = await User.find_one({"_id": user_id})  # Fixed to use find_one
    if not user:
        return JSONResponse(content={"message": "User not found"},
                            status_code=status.HTTP_401_UNAUTHORIZED)
    
    return JSONResponse(content={"message": f"Hello {user.username}, this is a protected route"}, 
                        status_code=status.HTTP_200_OK)