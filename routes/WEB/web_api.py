from fastapi import APIRouter, HTTPException, status, Depends
from db.schema import *
from fastapi.responses import JSONResponse
from .utils import create_access_token, hash_password, verify_token, store_share_token, get_share_data
from db.models import User, Applications
from decouple import config
from bson.objectid import ObjectId

router = APIRouter()


# Initialize Fernet with key from .env

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
async def get_user_profile(userid: str = Depends(verify_token)):
    if not userid:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    print(f"Looking for user with _id: {userid}")
    try:
        user = await User.find_one({"_id": ObjectId(userid) if userid.isalnum() else userid})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        print(f"User lookup error: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching user: {str(e)}")
    
    return JSONResponse({
        "username": user.username,
        "email": user.email
    })




@router.post("/sharelink/create")
async def create_collaborative_link(request: ApplicationRequest, userid: str = Depends(verify_token)):
    try:
        if not userid:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        print(f"Debug: Searching for user with username or _id: {userid}")

        user = await User.find_one({"_id": ObjectId(userid)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        app = await Applications.find_one({"app_name": request.app_name, "user_id.$id": user.id})
        if not app:
            raise HTTPException(status_code=404, detail="Application not found")

        # data = {"user_id": userid, "application_id": str(app.id)}
        # encrypted_data = fernet.encrypt(json.dumps(data).encode()).decode()
        share_token = store_share_token(userid, str(app.id))
        # collaborative_url = f"{config('BACKEND_URL')}/collaborate/{encrypted_data}"


        return JSONResponse({
            "status": status.HTTP_201_CREATED,
            "message": "Collaborative link created",
            "share_token": share_token
        })
        
    except Exception as e:
        print(f"Debug: User lookup error: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching user: {str(e)}")





#for testing purpose only
from pydantic import BaseModel

class TokenRequest(BaseModel):
    app_id: str
    user_id: str

@router.post("/test_set")
def test(data : TokenRequest):
    print(data)
    token = store_share_token(data.user_id, data.app_id)
    return {"share_token": token}

    
class Token(BaseModel):
    token: str

@router.get("/test_get")
def test_get(token: Token):
    data = get_share_data(token.token)
    return data