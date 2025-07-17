from pydantic import BaseModel, EmailStr
from typing import Optional, List
from enum import Enum
from datetime import date

# ----------Enums------------
class TreatmentStatus(str, Enum):
    ongoing = "ongoing"
    completed = "completed"
    planned = "planned"
    cancelled = "cancelled"

class TreatmentType(str, Enum):
    medication = "medication"
    therapy = "therapy"
    surgery = "surgery"
# ---------------------------

# ----------Schemas----------
class Treatment(BaseModel):
    name: str
    description: Optional[str] = None
    prescribing_specialist: Optional[str] = None
    specialist_observations: Optional[str] = None
    type: TreatmentType = TreatmentType.medication
    status: TreatmentStatus = TreatmentStatus.ongoing
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    outcome: Optional[str] = None
# ---------------------------