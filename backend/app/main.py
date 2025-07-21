from fastapi import FastAPI
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from routers import users, patients, specialists, auth, conditions, treatments, appointments, consultations

app = FastAPI(title="Medical Tracker API")

# Virtual environment: .venv\Scripts\activate
# Uvicorn server: uvicorn main:app --reload

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(patients.router, prefix="/patients", tags=["patients"])
app.include_router(specialists.router, prefix="/specialists", tags=["specialists"])
app.include_router(conditions.router, prefix="/conditions", tags=["conditions"])
app.include_router(treatments.router, prefix="/treatments", tags=["treatments"])
app.include_router(appointments.router, prefix="/appointments", tags=["appointments"])
app.include_router(consultations.router, prefix="/consultations", tags=["consultations"])

# Health check
@app.get("/")
async def health():
    return {"message": "Medical Tracker API is running"}

