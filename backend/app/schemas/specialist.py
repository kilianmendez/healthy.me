from pydantic import BaseModel, EmailStr
from typing import Optional, List
from enum import Enum
from datetime import date
from .user import User

from .treatment import Treatment
from .medication import Medication
from .consultation import Consultation

# ----------Enums------------
class UserRole(str, Enum):
    patient = "patient"
    specialist = "specialist"

class Gender(str, Enum):
    male = "male"
    female = "female"
    other = "other"
# ---------------------------

# ----------Specialist----------
class Specialist(User):
    role: UserRole = UserRole.specialist
    workplaces: Optional[List[str]] = []  # Lugar de trabajo del especialista
    available_hours: Optional[str] = None  # Horas disponibles para consultas
    specialties: Optional[List[str]] = []  # Especialidades del especialista
    biography: Optional[str] = None  # Biografía del especialista
    certifications: Optional[List[str]] = []  # Certificaciones del especialista
    patients: Optional[List[str]] = []  # IDs de pacientes asignados
    consultation_history: Optional[List[Consultation]] = []  # Consultas realizadas

class SpecialistCreate(Specialist):
    password: str  # Contraseña del especialista, necesaria para el registro

class SpecialistOut(Specialist):
    id: str  # ID del especialista, necesario para la salida del modelo

class SpecialistUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    gender: Optional[Gender] = None
    date_of_birth: Optional[date] = None
    disabled: Optional[bool] = None
    updated_at: Optional[date] = None
    avatar_url: Optional[str] = None
    workplaces: Optional[List[str]] = None
    available_hours: Optional[str] = None
    specialties: Optional[List[str]] = None
    biography: Optional[str] = None
    certifications: Optional[List[str]] = None
    patients: Optional[List[str]] = None
    consultation_history: Optional[List[Consultation]] = None
