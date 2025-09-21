from fastapi import FastAPI,HTTPException,status,Depends
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from auth import hash_password, verify_password, create_access_token, decode_access_token

app= FastAPI(title="SELFOPS web API")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

class LoginRequest(BaseModel):
    email: str
    password: str

user1={
    "email": "user@gmail.com",
    "password": hash_password("user123")
}

class SignupRequest(BaseModel):
    email: str
    password: str
    confirm_password: str


@app.post("/login")
def login(user: LoginRequest):
    if user.email != user1["email"] or not verify_password(user.password, user1["password"]):
        raise HTTPException(status_code=401, detail="Invalid emial or password")

    token = create_access_token({"sub": user.username})
    print(f"hashed_password: {user1['password']}")

    return JSONResponse({
        "status": status.HTTP_200_OK,
        "message": "Login successful",
        "access_token": token,
        "token_type": "bearer"
    }
    )

@app.post("/signup")
def signup(user:SignupRequest):
    if user.password != user.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    if user.email in user1:
        raise HTTPException(status_code=400, detail="User already exists")

    user1[user.email] = hash_password(user.password)

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

@app.get("/dashboard", response_model=ContainerStatus)
def dashboard(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return JSONResponse(container_status)
    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("web_main:app", port=8000, reload=True)