from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from enum import Enum

# ----------Enums------------
class PrescriptionFrequency(str, Enum):
    once_daily = "once_daily"
    twice_daily = "twice_daily"
    three_times_daily = "three_times_daily"
    every_x_hours = "every_x_hours"
    as_needed = "as_needed"
# ---------------------------

# ----------Schemas----------
class Prescription(BaseModel):
    medication_name: str
    dosage: str = Field(..., description="E.g., 500mg, 1 tablet, etc.")
    route: Optional[str] = Field(default="oral", description="How it's administered: oral, injection, etc.")
    frequency: PrescriptionFrequency = Field(..., description="How often to take it")
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    notes: Optional[str] = None
    prescribed_by: Optional[str] = None  # specialist_id
    prescribed_to: Optional[str] = None  # patient_id


