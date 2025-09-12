from fastapi import FastAPI
from routers import users, auth, patients, specialists, treatments, appointments, consultations, diagnoses
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(patients.router, prefix="/patients", tags=["Patients"])
app.include_router(specialists.router, prefix="/specialists", tags=["Specialists"])
app.include_router(diagnoses.router, prefix="/diagnoses", tags=["Diagnoses"])
app.include_router(treatments.router, prefix="/treatments", tags=["Treatments"])
app.include_router(appointments.router, prefix="/appointments", tags=["Appointments"])
app.include_router(consultations.router, prefix="/consultations", tags=["Consultations"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Medical Tracker API"}

