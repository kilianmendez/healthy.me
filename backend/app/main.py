from fastapi import FastAPI
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from routers import users, patients, specialists

app = FastAPI(title="Medical Tracker API")

# Include routers
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(patients.router, prefix="/patients", tags=["patients"])
app.include_router(specialists.router, prefix="/specialists", tags=["specialists"])


@app.get("/")
async def health():
    return {"message": "Medical Tracker API is running"}

