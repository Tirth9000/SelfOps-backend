from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from decouple import config
from .models import User, Applications, AppContainers, SharedResourcesModel

async def init_db():
    client = AsyncIOMotorClient(config("MONGODB_URL"))
    db = client.get_default_database()
    print("db connected")
    await init_beanie(
        database=db,
        document_models=[User, Applications, AppContainers, SharedResourcesModel]
    )
    print("Beanie models initialized successfully!")
