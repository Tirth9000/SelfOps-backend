from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from routes.WEB.auth import create_access_token, decode_access_token
from db.schema import LoginRequest, StatsRequest
from .service import authenticate_user, verify_token
from db.models import User, Applications, AppContainers

router = APIRouter()
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/cli/login")

@router.post("/login")
async def cli_login(user_data: LoginRequest, user: str = Depends(verify_token)):
    print('cli server')
    user = await authenticate_user(user_data.email, user_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"sub": user.username}) 
    return {
        "status": status.HTTP_200_OK,
        "message": "Login successful",
        "access_token": token,
        "token_type": "bearer"
    }



@router.post("/store_stats")
async def store_container_stats(data: StatsRequest):
    try:
        containers = data.containers
        user = await User.find_one({"email": "tirth@gmail.com"})
        user_app = Applications(app_name = data.app_name, user_id = user.id)
        app = await user_app.insert()

        if app:
            app_containers = [
                AppContainers(
                    app_id = app,
                    container_id = container.container_id,
                    container_name = container.container_name,
                    image = container.image,
                    status = container.status,
                    uptime = container.uptime,
                    restart_count = container.restart_count,
                    cpu_percent = container.cpu_percent,
                    memory_usage = container.memory_usage,
                    memory_limit = container.memory_limit,
                    network_io = container.network_io,
                    ports = container.ports,
                    health = container.health
                ) 
                for container in containers 
            ]

            await AppContainers.insert_many(app_containers)
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