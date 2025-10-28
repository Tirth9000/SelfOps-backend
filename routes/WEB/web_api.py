from fastapi import APIRouter, HTTPException, status, Depends
from db.schema import *
from fastapi.responses import JSONResponse
from .utils import create_access_token, hash_password, verify_token, store_share_token, get_share_data
from db.models import SharedResourcesModel, User, Applications,AppContainers
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
    
    token = create_access_token({"sub": str(db_user.id)}) 
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

# Get all apps owned by the current user
from fastapi import HTTPException, status, Depends
from fastapi.responses import JSONResponse
from bson import ObjectId

@router.get("/my-apps")
async def get_my_apps(userid: str = Depends(verify_token)):
    apps = await Applications.find(Applications.user_id.id == ObjectId(userid)).to_list()
    if not apps:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"apps": [], "conts": [], "message": "No apps found for this user."}
        )
    app_ids = [app.id for app in apps]
    conts = await AppContainers.find(AppContainers.app_id.id.in_(app_ids)).to_list()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "apps": [app.model_dump() for app in apps],
            "conts": [c.model_dump() for c in conts],
        }
    )


#Get all apps shared with the current user
@router.get("/shared-apps")
async def get_shared_apps(userid: str = Depends(verify_token)):
    shared_entries = await SharedResourcesModel.find(
        {"accessed_user_id": ObjectId(userid)}
    ).to_list()
    app_names = []
    for entry in shared_entries:
        app = await Applications.get(entry.app_id.id)
        if app:
            app_names.append(app.app_name)
        else:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"apps": [], "message": "No apps found for this user."}
            )    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "count": len(app_names),
            "apps": app_names
        }
    )


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


        return JSONResponse(status_code=status.HTTP_200_OK,
            content={
            "message": "Collaborative link created",
            "share_token": share_token
        })
        
    except Exception as e:
        print(f"Debug: User lookup error: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching user: {str(e)}")



# Share an application with the current user  Purpose:
        '''- Accept a share token and current user.
        - Verify that the token is valid and that the app belongs to the owner in the token.
        - If valid, create a SharedResourcesModel entry linking app and current user.'''
@router.post("/sharelink/join")
async def shared_resources(token: str, userid: str = Depends(verify_token)):
    share_data = get_share_data(token)
    if "error" in share_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=share_data["error"]
        )

    owner_user_id = share_data.get("user_id")
    app_id = share_data.get("app_id")

    user = await User.find_one({"_id": ObjectId(userid)})

    app_doc = await Applications.find_one({
        "_id": ObjectId(app_id),
        "user_id": ObjectId(owner_user_id)
    })

    if not app_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No matching application found for this owner and app ID"
        )

    existing = await SharedResourcesModel.find_one({
        "app_id": ObjectId(app_id),
        "accessed_user_id": ObjectId(userid)
    })
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already accessed this shared application"
        )

    shared_entry = SharedResourcesModel(
        app_id=app_doc,
        accessed_user_id=user,
    )
    await shared_entry.insert()

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Succesfully stored data in SharedResources model"
        }
    )

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