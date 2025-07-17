from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum
from datetime import date
from typing import List

from .condition import Condition
from .treatment import Treatment
from .medication import Medication
from .consultation import Consultation

# ----------Enums------------
class UserRole(str, Enum):
    patient = "patient"
    specialist = "specialist"
    admin = "admin"

class Gender(str, Enum):
    male = "male"
    female = "female"
    other = "other"
# ---------------------------

# ----------Schemas----------
class User(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    gender: Optional[Gender] = None
    date_of_birth: Optional[date] = None
    role: UserRole = UserRole.patient
    disabled: Optional[bool] = False
    created_at: Optional[date] = None  # Fecha de creación del usuario
    updated_at: Optional[date] = None  # Fecha de última actualización del usuario
    avatar_url: Optional[str] = None  # URL de la imagen del avatar del usuario

class UserOut(User):
    id: str

class UserCreate(User):
    password: str  # Contraseña del usuario, necesaria para el registro
# ---------------------------

# ----------Patient----------
class Patient(User):
    role: UserRole = UserRole.patient
    phone_number: Optional[str] = None  # Número de teléfono
    emergency_contact: Optional[str] = None  # Contacto de emergencia
    conditions: Optional[List[Condition]] = []
    treatments: Optional[List[Treatment]] = []
    medications: Optional[List[Medication]] = []
    allergies: Optional[List[str]] = []  # Alergias conocidas
    appointments: Optional[List[str]] = []  # IDs de citas/appointments
    consultation_history: Optional[List[Consultation]] = []
    prescriptions: Optional[List[Medication]] = []  # Recetas digitales generadas

# ----------Specialist----------
class Specialist(User):
    role: UserRole = UserRole.specialist
    workplaces: Optional[List[str]] = []  # Lugar de trabajo del especialista
    available_hours: Optional[str] = None  # Horas disponibles para consultas
    specialties: Optional[List[str]] = []  # Especialidades del especialista
    biography: Optional[str] = None  # Biografía del especialista
    certifications: Optional[List[str]] = []  # Certificaciones del especialista
    patients: Optional[List[str]] = []  # IDs de pacientes asignados
    appointments: Optional[List[str]] = []  # IDs de citas/appointments
    prescriptions: Optional[List[Medication]] = []  # Recetas digitales generadas
    consultation_history: Optional[List[Consultation]] = []  # Consultas realizadas

class SpecialistCreate(Specialist):
    password: str  # Contraseña del especialista, necesaria para el registro