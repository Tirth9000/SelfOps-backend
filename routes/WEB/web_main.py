from fastapi import APIRouter, FastAPI, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from .auth import create_access_token, decode_access_token
from db.models import User
import subprocess
import re
from fastapi import APIRouter

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")  # Matches CLI endpoint

class UserRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

class OrganizationRequest(BaseModel):
    user_id: str
    organization_name: str

class LoginRequest(BaseModel):
    email: str
    password: str

class ApplicationRequest(BaseModel):
    organization_id: str
    app_name: str

class ContainerActionRequest(BaseModel):
    application_id: str
    container_name: str
    port: str
    image_name: str
    image_tag: str
    environment: dict
    volumes: list[str]

@router.post("/register")
async def register(user: UserRequest):
    existing = await User.find_one({"email": user.email})
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    
    new_user = User(username=user.username, email=user.email, password=user.password)  # Include password
    
    await new_user.insert()
    return JSONResponse({
        "status": status.HTTP_201_CREATED,
        "message": "User registered successfully",
        "email": user.email
    })

@router.post("/login")
async def login(user: LoginRequest):
    db_user = await User.find_one({"email": user.email})
    if not db_user or not db_user.verify_password(user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"sub": db_user.username}) 
    return JSONResponse({
        
        "message": "Login successful",
        "access_token": token,
        "token_type": "bearer"
        }
    )



class SignupRequest(BaseModel):
    username: str
    email: str
    password: str
    confirm_password: str
    
@router.post("/signup")
def signup(user:SignupRequest):
    if user.password != user.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    if user.email in users:
        raise HTTPException(status_code=400, detail="User already exists")

    users[user.email] = {
        "username": user.username,
        "email": user.email,
        "password": hash_password(user.password)
    }
    print(users)
    

@router.get("/user/profile", response_model=dict)
async def get_user_profile(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user_id = payload.get("sub")
    print(f"Looking for user with _id: {user_id}")  # Debug the ID
    from bson.objectid import ObjectId  # Import if using MongoDB ObjectId
    try:
        user = await User.find_one({"_id": ObjectId(user_id) if user_id.isalnum() else user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        print(f"User lookup error: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching user: {str(e)}")
    
    return JSONResponse({
        "username": user.username,
        "email": user.email
    })


@router.post("/organization/create")
async def create_organization(org: OrganizationRequest, token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    # Implement organization creation logic
    return JSONResponse({
        "status": status.HTTP_201_CREATED,
        "message": "Organization created successfully",
        "organization_id": "new_org_id"  # Placeholder
    })

@router.get("/dashboard/info", response_model=dict)
async def get_dashboard_info(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    # Hardcoded initial stats (to be replaced with real data later)
    return JSONResponse({
        "registered_users": 5,
        "active_containers": 0
    })

container_status = {
    "image": "nginx:1.26",
    "uptime": "2h 14m",
    "restarts": 1,
    "cpu": "12.5%",
    "memory": "256MB / 1GB",
    "net_io": "12.4MB / 8.9MB",
    "ports": "80→8080, 443→8443"
}



@router.get("/container/status", response_model=dict)
async def get_container_status(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    # For now, revert to static data to match old behavior
    return JSONResponse(container_status)
