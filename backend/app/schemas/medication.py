from pydantic import BaseModel, EmailStr
from typing import Optional, List
from enum import Enum
from datetime import date

# ----------Enums------------

# ---------------------------

# ----------Schemas----------
class Medication(BaseModel):
    name: str
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
# ---------------------------