from fastapi import FastAPI, Depends, HTTPException, status
from db.database import base, engine
from db import models, schema

models.base.metadata.create_all(bind=engine)

app = FastAPI()

users = {
    "user1": "password1"
    }

@app.post('/login')
def cli_lojgin(user: schema.User):
    print("Login request received")
    username = Depends(user.username)
    password = Depends(user.password)
    if username not in users or users[username] != password:
        raise HTTPException(status=status.HTTP_400_BAD_REQUEST, detail="Invalid username or password")
    return {"message": "Login successful", status: status.HTTP_200_OK}