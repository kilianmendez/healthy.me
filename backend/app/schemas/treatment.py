from pydantic import BaseModel, EmailStr
from typing import Optional, List
from enum import Enum
from datetime import date
from .prescription import Prescription

# ----------Enums------------
class TreatmentStatus(str, Enum):
    ongoing = "ongoing"
    completed = "completed"
    planned = "planned"
    cancelled = "cancelled"
# ---------------------------

# ----------Schemas----------
class Treatment(BaseModel):
    name: str
    description: Optional[str] = None
    observations: Optional[str] = None
    type: Optional[str] = None  # e.g., "physical therapy", "surgery", etc.
    prescribed_by: Optional[str] = None  # ID of the specialist who prescribed
    prescribed_to: Optional[str] = None  # ID of the patient
    prescriptions: Optional[List[Prescription]] = None
    status: TreatmentStatus = TreatmentStatus.ongoing
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    outcome: Optional[str] = None

class TreatmentOut(Treatment):
    id: str  # ID of the treatment, necessary for the output model

class TreatmentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    observations: Optional[str] = None
    type: Optional[str] = None
    prescribed_by: Optional[str] = None
    prescribed_to: Optional[str] = None
    prescriptions: Optional[List[Prescription]] = None
    status: Optional[TreatmentStatus] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    outcome: Optional[str] = None
# ---------------------------