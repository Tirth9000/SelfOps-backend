from fastapi import FastAPI
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from db.models import User
from routes.CLI.cli_main import router as cli_router
from routes.WEB.web_main import router as web_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Allow your frontend origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)
# Database connection
async def init_db():
    client = AsyncIOMotorClient("mongodb://localhost:27017/")
    await init_beanie(database=client.SelfOpsDB, document_models=[User])

# Startup event to initialize database
@app.on_event("startup")
async def on_startup():
    await init_db()

# Include routers
app.include_router(cli_router, prefix="/cli", tags=["cli"])
app.include_router(web_router, tags=["web"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)