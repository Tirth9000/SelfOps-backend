from fastapi import APIRouter, HTTPException, status
from backend.db.database import base, engine
from backend.db import models, schema
#also import get_db and from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
models.base.metadata.create_all(bind=engine)

router = APIRouter()

#instead of user dict connect to model DB
users = {                    
    "aaditya": "password1"
    }

@router.post('/login')
def cli_login(user: schema.User):
    print("Login request received")
    username = user.username #use Depend
    password = user.password #use Depend
    if username not in users or users[username] != password:
        return {
            "error": "Invalid username or password",
            "status": status.HTTP_400_BAD_REQUEST
        }
    return JSONResponse(
    content={"message": "Login successful"},
        status_code=status.HTTP_200_OK
    )

