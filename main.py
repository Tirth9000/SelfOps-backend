from fastapi import FastAPI
from contextlib import asynccontextmanager
from backend.routes.CLI.auth_api import router as cli_router
from backend.routes.WEB.web_api import router as web_router
from fastapi.middleware.cors import CORSMiddleware
from socket_server import socket_app
from backend.db.database import init_db
import os


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
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:socket_app", host="0.0.0.0", port=port, reload=False)