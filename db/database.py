from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from decouple import config
from .models import User, Applications, AppContainers,SharedResourcesModel

async def init_db():
    client = AsyncIOMotorClient(config("MONGODB_URI"))
    print('db connected')
    db = client.get_default_database()
    await init_beanie(database=db, document_models=[User, Applications, AppContainers,SharedResourcesModel])  