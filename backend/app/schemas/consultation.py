from pydantic import BaseModel, EmailStr
from typing import Optional, List
from enum import Enum
from datetime import date

# ----------Enums------------
class ConsultationStatus(str, Enum):
    scheduled = "scheduled"
    completed = "completed"
    cancelled = "cancelled"
# ---------------------------

# ----------Schemas----------
class Consultation(BaseModel):
    date: date
    specialist: Optional[str] = None
    status: ConsultationStatus = ConsultationStatus.scheduled
    notes: Optional[str] = None
    reason: Optional[str] = None
    follow_up_required: Optional[bool] = False
# ---------------------------