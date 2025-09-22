from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

# ----------Enums------------
class AppointmentStatus(str, Enum):
    pending = "pending"
    scheduled = "scheduled"
    cancelled = "cancelled"
    completed = "completed"
# ---------------------------

# ----------Schemas----------

class Appointment(BaseModel):
    date: datetime
    specialist_id: str
    patient_id: str
    reason: Optional[str] = None
    notes: Optional[str] = None
    location: Optional[str] = None
    status: AppointmentStatus = AppointmentStatus.scheduled

class AppointmentOut(Appointment):
    id: str  # Aseguramos que siempre se devuelva

class AppointmentUpdate(BaseModel):
    date: Optional[datetime] = None
    specialist_id: Optional[str] = None
    patient_id: Optional[str] = None
    reason: Optional[str] = None
    notes: Optional[str] = None
    location: Optional[str] = None
    status: Optional[AppointmentStatus] = None
