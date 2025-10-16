from fastapi import APIRouter, HTTPException, status, Depends
from db.schema import *
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from .auth import create_access_token, decode_access_token, hash_password
from db.models import User, Applications
from cryptography.fernet import Fernet
from decouple import config
import json
from bson.objectid import ObjectId

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/web/login")

# Initialize Fernet with key from .env
FERNET_KEY = config("FERNET_KEY")
fernet = Fernet(FERNET_KEY.encode())  

@router.post("/register")
async def register(user: SignupRequest):
    existing = await User.find_one({"email": user.email})
    if existing:
        raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail="User already exists")
    
    new_user = User(username=user.username, email=user.email, password=hash_password(user.password))  # Include password
    
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

users = {
    "user1": {
        "username": "user1",
        "email": "user1@gmail.com",
        "password": "pass123",
    },
}



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


@router.post("/collaborate/create")
async def create_collaborative_link(request: ApplicationRequest, token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id = payload.get("sub")
    print(f"Debug: Searching for user with username or _id: {user_id}")

    try:
        if all(c in '0123456789abcdefABCDEF' for c in user_id) and len(user_id) == 24:
            user = await User.find_one({"_id": ObjectId(user_id)})
        else:
            user = await User.find_one({"username": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        print(f"Debug: User lookup error: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching user: {str(e)}")

    # ✅ FIXED QUERY
    app = await Applications.find_one({"app_name": request.app_name, "user_id.$id": user.id})
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    data = {"user_id": user.username, "application_id": str(app.id)}
    encrypted_data = fernet.encrypt(json.dumps(data).encode()).decode()
    collaborative_url = f"{config('BACKEND_URL')}/collaborate/{encrypted_data}"

    return JSONResponse({
        "status": status.HTTP_201_CREATED,
        "message": "Collaborative link created",
        "url": collaborative_url
    })
