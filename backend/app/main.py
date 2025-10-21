from fastapi import FastAPI
from routers import users, auth, patients, specialists, treatments, appointments, consultations, diagnoses
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from PIL import Image
from db.seeder import seed_db

app = FastAPI()

@app.on_event("startup")
def startup_event():
    """
    Check for and create placeholder avatars on startup.
    """
    placeholder_dir = "uploads/avatars/placeholder"
    patient_avatar = os.path.join(placeholder_dir, "default_patient.jpg")
    specialist_avatar = os.path.join(placeholder_dir, "default_specialist.jpg")
    
    # The greenish-cyan color (Turquoise)
    color = (64, 224, 208) 
    image_size = (200, 200)

    if not os.path.exists(placeholder_dir):
        os.makedirs(placeholder_dir)

    if not os.path.exists(patient_avatar):
        img = Image.new('RGB', image_size, color)
        img.save(patient_avatar, 'JPEG')

    if not os.path.exists(specialist_avatar):
        img = Image.new('RGB', image_size, color)
        img.save(specialist_avatar, 'JPEG')

    seed_db()

# Static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Middleware
# Note: Skipping the CORS fix as requested by the user.
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