from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum
from datetime import date
from typing import List
from .user import User

from .condition import Condition
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
    appointments: Optional[List[str]] = []  # IDs de citas/appointments
    prescriptions: Optional[List[Medication]] = []  # Recetas digitales generadas
    consultation_history: Optional[List[Consultation]] = []  # Consultas realizadas

class SpecialistCreate(Specialist):
    password: str  # Contraseña del especialista, necesaria para el registro

class SpecialistOut(Specialist):
    id: str  # ID del especialista, necesario para la salida del modelo