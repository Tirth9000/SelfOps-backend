from fastapi import FastAPI, Depends, HTTPException
from Database.database import base, engine
from Database import models, schema

models.base.metadata.create_all(bind=engine)

app = FastAPI()

def cli_login():
    return "welcome to the  web login page"