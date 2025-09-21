from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from enum import Enum
from datetime import date
from typing import List
from .user import User
from .treatment import Treatment
from .consultation import Consultation

# ----------Enums------------
class UserRole(str, Enum):
    patient = "patient"
    specialist = "specialist"

class Gender(str, Enum):
    male = "male"
    female = "female"
    other = "other"

# ----------Patient----------
class Patient(User):
    role: UserRole = UserRole.patient
    patient_code: Optional[str] = Field(None, unique=True, description="Unique code for patient to share with specialists.")
    phone_number: Optional[str] = None  # Número de teléfono
    emergency_contact: Optional[str] = None  # Contacto de emergencia
    treatments: Optional[List[Treatment]] = []
    medications: Optional[List[str]] = []
    allergies: Optional[List[str]] = []  # Alergias conocidas
    consultation_history: Optional[List[Consultation]] = []

class PatientRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    gender: Optional[Gender] = None
    date_of_birth: Optional[date] = None

# Public model for general lists
class PatientPublic(BaseModel):
    id: str
    username: str
    full_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    avatar_url: Optional[str] = None
    gender: Optional[Gender] = None



# Complete model for authorized users (owner, assigned specialist, admin)
class PatientPrivate(Patient):
    id: str

class PatientUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    gender: Optional[Gender] = None
    date_of_birth: Optional[date] = None
    disabled: Optional[bool] = None
    updated_at: Optional[date] = None
    avatar_url: Optional[str] = None
    phone_number: Optional[str] = None
    emergency_contact: Optional[str] = None
    treatments: Optional[List[Treatment]] = None
    medications: Optional[List[str]] = None
    allergies: Optional[List[str]] = None
    consultation_history: Optional[List[Consultation]] = None

class PatientSelfUpdate(BaseModel):
    username: Optional[str] = None
    full_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    avatar_url: Optional[str] = None
    phone_number: Optional[str] = None
    emergency_contact: Optional[str] = None
    allergies: Optional[List[str]] = None
    medications: Optional[List[str]] = None
