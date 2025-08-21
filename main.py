from fastapi import FastAPI
from .routes import cli_main, web_main


app = FastAPI(title = "SELFOPS BDE")

app.include_router(cli_main.router, prefix="/cli", tags=["CLI"])