from fastapi import FastAPI
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from db.models import User, Applications
from routes.CLI.cli_main import router as cli_router
from routes.WEB.web_main import router as web_router
from fastapi.middleware.cors import CORSMiddleware
from socket_server import socket_app
from db.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    await init_db()
    yield
    # Shutdown code (if any)


app = FastAPI(lifespan=lifespan)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow your frontend origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

socket_app.other_asgi_app = app

# Include routers
app.include_router(cli_router, prefix="/cli", tags=["cli"])
app.include_router(web_router, prefix="/web", tags=["web"])




if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:socket_app", host="localhost", port=8000, reload=True)