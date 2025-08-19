from fastapi import FastAPI, Depends, HTTPException, status
from backend.db.database import base, engine
from backend.db import models, schema
#also import get_db and from sqlalchemy.orm import Session

models.base.metadata.create_all(bind=engine)

app = FastAPI()
#instead of user dict connect to model DB
users = {                    
    "aaditya": "password1"
    }

@app.post('/login')
def cli_login(user: schema.User):
    print("Login request received")
    username = user.username #use Depend
    password = user.password #use Depend
    if username not in users or users[username] != password:
        raise HTTPException(status=status.HTTP_400_BAD_REQUEST, detail="Invalid username or password")
    return {
    "message": "Login successful",
    "status": status.HTTP_200_OK
    }
