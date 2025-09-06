#pydantic request/response validators.
from pydantic import BaseModel, Field


class User(BaseModel):
    # username: str = Field(..., min_length=6, max_length=20, description="Username must be between 6 and 20 characters.")
    # password: str = Field(..., min_length=8, max_length=50, description="Password must be between 8 and 50 characters.")
    username: str
    password: str