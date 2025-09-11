from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum
from datetime import date
from typing import List

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

class UserDb(User):
    id: str
    password: str
# ---------------------------