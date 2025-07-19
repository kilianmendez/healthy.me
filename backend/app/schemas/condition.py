from pydantic import BaseModel, EmailStr
from typing import Optional, List
from enum import Enum
from datetime import date

# ----------Enums------------
class ConditionStatus(str, Enum):
    active = "active"
    resolved = "resolved"
    inactive = "inactive"
# ---------------------------

# ----------Schemas----------
class Condition(BaseModel):
    name: str
    description: Optional[str] = None
    symptoms: Optional[List[str]] = None
    observations: Optional[str] = None
    diagnosed_by: Optional[str] = None  # ID of the specialist who diagnosed
    diagnosed_to: Optional[str] = None  # ID of the patient
    diagnosed_at: Optional[date] = None
    status: ConditionStatus = ConditionStatus.active

class ConditionOut(Condition):
    id: str
# ---------------------------