from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TimeOffBase(BaseModel):
    start_datetime: datetime
    end_datetime: datetime
    reason: Optional[str] = None

class TimeOffCreate(TimeOffBase):
    pass

class TimeOffOut(TimeOffBase):
    id: str
    specialist_id: str
