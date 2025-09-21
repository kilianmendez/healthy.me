from pydantic import BaseModel, EmailStr
from typing import Optional, List, Union
from enum import Enum
import datetime
from .treatment import Treatment, TreatmentOut
from .diagnosis import DiagnosisCreate, DiagnosisOut

# ----------Enums------------
# ---------------------------

# ----------Schemas----------
class Consultation(BaseModel):
    date: datetime.date
    specialist_id: Optional[str] = None         # id real del especialista
    patient_id: Optional[str] = None            # si consultas se guardan fuera del modelo paciente
    reason: Optional[str] = None
    notes: Optional[str] = None
    diagnosis: Optional[Union[DiagnosisCreate, str]] = None # diagnóstico realizado
    follow_up_required: Optional[bool] = False 
    treatments: Optional[List[Treatment]] = None
    appointment_id: Optional[str] = None        # relación directa con cita (si aplica)

class ConsultationOut(Consultation):
    id: str
    diagnosis: Optional[DiagnosisOut] = None
    treatments: Optional[List[TreatmentOut]] = []

class ConsultationUpdate(BaseModel):
    date: Optional[datetime.date] = None
    specialist_id: Optional[str] = None
    patient_id: Optional[str] = None
    reason: Optional[str] = None
    notes: Optional[str] = None
    diagnosis: Optional[str] = None
    follow_up_required: Optional[bool] = None 
    treatments: Optional[List[Treatment]] = None

# ---------------------------

class ConsultationOutSimple(ConsultationOut):
    treatments: Optional[List[str]] = None
