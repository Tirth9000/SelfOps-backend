from fastapi import APIRouter, Request, Response, HTTPException, status, Depends
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from .auth import hash_password, verify_password, create_access_token, decode_access_token

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


users={
    "user@gmail.com" : {
        "username": "user1",
        "email": "user@gmail.com",
        "password": hash_password("user123")
        }
    }


class LoginRequest(BaseModel):
    email: str
    password: str
    
@router.post("/login")
def login(user: LoginRequest):
    if user.email not in users and verify_password(user.password, users[user.email]['password']):
        raise HTTPException(status_code=401, detail="Invalid emial or password")

    token = create_access_token({"sub": users[user.email]["username"]})
    print(f"hashed_password: {users[user.email]['password']}")

    return JSONResponse({
        "status": status.HTTP_200_OK,
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

    return JSONResponse({
        "status": status.HTTP_201_CREATED,
        "message": "User registered successfully",
        "email": user.email
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
class ContainerStatus(BaseModel):
    image:str
    uptime: str
    restarts : int
    cpu : str   
    memory: str
    net_io: str
    ports: str

@router.get("/dashboard", response_model=ContainerStatus)
def dashboard(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return JSONResponse(container_status)
    
@router.get("/test")
def test_root():
    return {"message": "Web route is working!"}
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("web_main:app", port=8000, reload=True)