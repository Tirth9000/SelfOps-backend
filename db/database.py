from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from decouple import config
from .models import User  # Import other models like Container if added later

async def init_db():
    client = AsyncIOMotorClient(config("MONGODB_URI"))
    await init_beanie(database=client.get_default_database(), document_models=[User])  # Add more models as needed