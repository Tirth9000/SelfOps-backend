from fastapi import FastAPI
from routes.CLI import cli_main
from routes.WEB import web_main


app = FastAPI(title = "SELFOPS BDE")

app.include_router(cli_main.router, prefix="/cli", tags=["CLI"])



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", port=8000, reload=True)