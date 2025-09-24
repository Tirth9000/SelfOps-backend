from fastapi import FastAPI
from routes.CLI import cli_main
from socket_server import socket_app
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title = "SELFOPS BDE")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



app.include_router(cli_main.router, prefix="/cli", tags=["CLI"])


socket_app.other_asgi_app = app



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:socket_app", port=8000, reload=True)