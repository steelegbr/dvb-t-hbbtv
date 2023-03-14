from dotenv import dotenv_values
from fastapi import APIRouter, FastAPI
from log import log_router
from pymongo import MongoClient

config = dotenv_values(".env")

app = FastAPI()
prefix_router = APIRouter(prefix="/api")


@app.on_event("startup")
def startup_db_client():
    app.mongodb_client = MongoClient(config["ATLAS_URI"])
    app.database = app.mongodb_client[config["DB_NAME"]]


@app.on_event("shutdown")
def shutdown_db_client():
    app.mongodb_client.close()


prefix_router.include_router(log_router, prefix="/log")
app.include_router(prefix_router)
