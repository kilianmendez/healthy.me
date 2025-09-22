# schemas/diagnosis.py
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
from datetime import date

class DiagnosisStatus(str, Enum):
    active = "active"
    resolved = "resolved"
    inactive = "inactive"

class Diagnosis(BaseModel):
    condition_name: str
    patient_id: str
    specialist_id: Optional[str] = None
    diagnosed_at: date
    symptoms: Optional[List[str]] = []
    observations: Optional[str] = None
    status: DiagnosisStatus = DiagnosisStatus.active

class DiagnosisCreate(Diagnosis):
    pass

class DiagnosisOut(Diagnosis):
    id: str

class DiagnosisUpdate(BaseModel):
    diagnosed_at: Optional[date] = None
    symptoms: Optional[List[str]] = None
    observations: Optional[str] = None
    status: Optional[DiagnosisStatus] = None
