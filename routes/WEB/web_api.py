from fastapi import APIRouter, HTTPException, status, Depends
from db.schema import *
from fastapi.responses import JSONResponse
from .utils import *
from db.models import SharedResourcesModel, User, Applications, AppContainers
from bson.objectid import ObjectId
from datetime import timedelta
import json

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
    
    access_token = create_access_token({"sub": str(db_user.id)}) 
    refresh_token = create_refresh_token({"sub": str(db_user.id)})

    data = {"refresh_token": refresh_token}
    r_client.setex(str(db_user.id), timedelta(days=7), json.dumps(data))

    return JSONResponse({
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer"
        }
    )


@router.post("/token/refresh")
async def refresh_token_endpoint(old_token: GetOldToken):
    try:
        payload = decode_access_token(old_token.old_access_token)
        user_id: str = payload.get("sub")
        stored_refresh_token = await r_client.get(user_id)
        if stored_refresh_token is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid refresh token")
        
        new_access_token = create_access_token({"sub": user_id})
        return JSONResponse({
            "access_token": new_access_token,
            "token_type": "bearer"
        })
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Refresh token is invalid or expired")



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



@router.get("/my-apps")
async def get_my_apps(userid: str = Depends(verify_token)):
    apps = await Applications.find(Applications.user_id.id == ObjectId(userid)).to_list()
    if not apps:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"apps": [], "message": "No apps found for this user."}
        )
    return {"apps": apps, "status_code": status.HTTP_200_OK}



@router.get("/app/containers/{app_id}")
async def get_app_containers(app_id: str): 
    if not app_id:
        raise HTTPException(status_code=400, detail="app_id is required")
    
    app_containers = await AppContainers.find(AppContainers.app_id.id == ObjectId(app_id)).to_list()
    return {"app_containers": app_containers, "status_code": status.HTTP_200_OK}
    


#Get all apps shared with the current user
@router.get("/shared-apps")
async def get_shared_apps(userid: str = Depends(verify_token)):
    shared_apps = await SharedResourcesModel.find(
        SharedResourcesModel.accessed_user_id.id == ObjectId(userid)
        ).to_list()

    if not shared_apps:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"shared_apps": [], "message": "No shared apps found for this user."}
        )
    
    apps = []
    for app in shared_apps:
        apps.append(await app.app_id.fetch())
    
    return {"apps": apps, "status_code": status.HTTP_200_OK}



@router.post("/sharelink/create")
async def create_collaborative_link(app_data: SharedTokenSchema, userid: str = Depends(verify_token)):
    try:
        if not userid:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        print(f"Debug: Searching for user with username or _id: {userid}")

        user = await User.find_one({"_id": ObjectId(userid)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        app = await Applications.find_one(Applications.id == ObjectId(app_data.app_id))
        if not app:
            raise HTTPException(status_code=404, detail="Application not found")

        share_token = store_share_token(userid, str(app.id))


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
async def shared_resources(token_data: SharedJoinSchema, userid: str = Depends(verify_token)):
    try:
        share_data = get_share_data(token_data.share_token)
        if "error" in share_data:
            return HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=share_data["error"]
            )

        owner_user_id = share_data.get("user_id")
        application_id = share_data.get("app_id")

        user = await User.find_one({"_id": ObjectId(userid)})

        if owner_user_id == userid:
            return JSONResponse(
                status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                content={
                    "message": "You are the owner of this application, no need to join."
                }
            )

        app_doc = await Applications.find_one(Applications.id == ObjectId(application_id), Applications.user_id.id == ObjectId(owner_user_id))

        if not app_doc:
            return HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No matching application found for this owner and app ID"
            )

        existing = await SharedResourcesModel.find_one(SharedResourcesModel.app_id.id == ObjectId(application_id), SharedResourcesModel.accessed_user_id.id == ObjectId(userid))
        print(existing)
        if existing:
            return HTTPException(
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
    except Exception as e:
        print(f"Debug: Error in sharing application: {e}")
        return HTTPException(status_code=500, detail=f"Error sharing application: {str(e)}")






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