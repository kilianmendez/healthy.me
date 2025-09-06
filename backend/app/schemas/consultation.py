from pydantic import BaseModel, EmailStr
from typing import Optional, List
from enum import Enum
import datetime
from .treatment import Treatment

# ----------Enums------------
# ---------------------------

# ----------Schemas----------
class Consultation(BaseModel):
    date: datetime.date
    specialist_id: Optional[str] = None         # id real del especialista
    patient_id: Optional[str] = None            # si consultas se guardan fuera del modelo paciente
    reason: Optional[str] = None
    notes: Optional[str] = None
    diagnosis: Optional[str] = None             # diagnóstico realizado
    follow_up_required: Optional[bool] = False 
    prescriptions: Optional[List[str]] = None
    treatments: Optional[List[str]] = None
    appointment_id: Optional[str] = None        # relación directa con cita (si aplica)

class ConsultationOut(Consultation):
    id: str

class ConsultationUpdate(BaseModel):
    date: Optional[datetime.date] = None
    specialist_id: Optional[str] = None
    patient_id: Optional[str] = None
    reason: Optional[str] = None
    notes: Optional[str] = None
    diagnosis: Optional[str] = None
    follow_up_required: Optional[bool] = None 
    prescriptions: Optional[List[str]] = None
    treatments: Optional[List[str]] = None

# ---------------------------