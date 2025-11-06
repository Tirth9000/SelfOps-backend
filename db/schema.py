from pydantic import BaseModel, EmailStr, Field
from typing import List

class User(BaseModel):
    username: str
    password: str

class SignupRequest(BaseModel):
    username: str = Field(..., min_length=5, max_length=10)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=20)


class ContainerStats(BaseModel):
    container_id: str
    container_name: str
    image: str
    status: str
    uptime: str
    restart_count: int
    cpu_percent: float
    memory_usage: int
    memory_limit: int
    network_io: dict
    ports: dict
    health: str
    
    class Config:
        extra = "allow"

        
class StatsRequest(BaseModel):
    app_name: str
    containers: List[ContainerStats]

    class Config:
        extra = "allow"

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(...)


class SharedResourcesSchema(BaseModel):
    app_id: str
    accessed_user_id:str    

class SharedTokenSchema(BaseModel):
    app_id: str

class SharedJoinSchema(BaseModel):
    share_token: str

class GetOldToken(BaseModel):
    old_access_token: str