from pydantic import BaseModel, EmailStr, Field, model_validator

class User(BaseModel):
    username: str
    password: str

class SignupRequest(BaseModel):
    username: str = Field(..., min_length=5, max_length=10)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=20)


# class OrganizationRequest(BaseModel):
#     user_id: str
#     organization_name: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(...)

class ApplicationRequest(BaseModel):
    organization_id: str
    app_name: str

class ContainerActionRequest(BaseModel):
    application_id: str
    container_name: str
    port: str
    image_name: str
    image_tag: str
    environment: dict
    volumes: list[str]

class SignupRequest(BaseModel):
    username: str
    email: str
    password: str
    confirm_password: str
    