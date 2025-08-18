from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .database import base

class User(base): 
    __tablename__ = "users"
    
    username = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)