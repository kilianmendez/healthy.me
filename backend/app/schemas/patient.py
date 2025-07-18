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

class PatientCreate(Patient):
    password: str  # Contraseña del paciente, necesaria para el registro

class PatientOut(Patient):
    id: str  # ID del paciente, necesario para la salida del modelo