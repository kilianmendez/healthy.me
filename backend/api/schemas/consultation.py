from pydantic import BaseModel, EmailStr
from typing import Optional, List, Union
from enum import Enum
import datetime
from api.schemas.treatment import Treatment, TreatmentOut
from api.schemas.diagnosis import DiagnosisCreate, DiagnosisOut

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



# ---------------------------

class ConsultationOutSimple(ConsultationOut):
    treatments: Optional[List[str]] = None
