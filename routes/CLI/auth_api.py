from bson import ObjectId
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from backend.routes.CLI.utils import cli_create_access_token
from backend.db.schema import LoginRequest, StatsRequest
from .utils import authenticate_user, verify_token
from backend.db.models import User, Applications, AppContainers

router = APIRouter()


@router.post("/login")
async def cli_login(user_data: LoginRequest):
    user = await authenticate_user(user_data.email, user_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = cli_create_access_token({"sub": str(user.id)}) 
    
    return {
        "status": status.HTTP_200_OK,
        "message": "Login successful",
        "username": user.username,
        "access_token": token,
        "token_type": "bearer"
    }



@router.post("/store_stats")
async def store_container_stats(data: StatsRequest, userid: str = Depends(verify_token)):
    try:
        containers = data.containers
        user = await User.find_one({"_id": ObjectId(userid)})
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
            return JSONResponse(content={"app_id": str(app.id), "message": "Container stats stored successfully"},
                                status_code=status.HTTP_201_CREATED)
    except Exception as e:
        return JSONResponse(content={"message": f"Error storing container stats: {e}"},
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)



#test
@router.get("/test_token")
async def test_token(userid : str = Depends(verify_token)):
    print(userid)
    user = await User.find_one({"_id": ObjectId(userid)})
    if user: 
        print(user)
        return {"user_id": userid, "username": user.username}
    raise HTTPException(status_code=404, detail="User not found")
