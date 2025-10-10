from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from routes.WEB.auth import create_access_token, decode_access_token
from db.schema import LoginRequest, StatsRequest
from .service import authenticate_user
from db.models import User, Applications, ContainerStats

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/cli/login")



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


@router.post("/store_stats")
async def store_container_stats(data: StatsRequest):
    # print(data)
    containers = data.containers
    try:
        user = await User.find_one({"email": "user1@gmail.com"})
        print(user)
        user_app = Applications(app_name = data.app_name, user_id = user.id)
        app = await user_app.insert()
        print(app)

        if app:
            count = 1
            for container in containers:
                print(count)
                count +=1 
                # await new_container_stats.insert()
            return JSONResponse(content={"message": "Container stats stored successfully"},
                                status_code=status.HTTP_201_CREATED)
    except Exception as e:
        return JSONResponse(content={"message": f"Error storing container stats: {e}"},
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)




# @router.get('/protected')
# async def protected_route(token: str = Depends(oauth2_scheme)):
#     print("Protected route accessed")
#     token_data = decode_access_token(token)
#     if not token_data:
#         return JSONResponse(content={"message": "Invalid or expired token"},
#                             status_code=status.HTTP_401_UNAUTHORIZED)
    
#     user_id = token_data.get("sub")
#     user = await User.find_one({"_id": user_id})  # Fixed to use find_one
#     if not user:
#         return JSONResponse(content={"message": "User not found"},
#                             status_code=status.HTTP_401_UNAUTHORIZED)
    
#     return JSONResponse(content={"message": f"Hello {user.username}, this is a protected route"}, 
#                         status_code=status.HTTP_200_OK)