from pydantic import BaseModel
from typing import Optional, List
from datetime import time, datetime


class WeeklyAvailabilityBase(BaseModel):
    day_of_week: int  # 0 = Monday, 6 = Sunday
    start_time: time
    end_time: time

class WeeklyAvailabilityCreate(WeeklyAvailabilityBase):
    pass

class WeeklyAvailabilityOut(WeeklyAvailabilityBase):
    id: str
    specialist_id: str

class WeeklyAvailabilityCreateList(BaseModel):
    availabilities: List[WeeklyAvailabilityCreate]

class WeeklyAvailabilityOutList(BaseModel):
    availabilities: List[WeeklyAvailabilityOut]

class BlockedSlotBase(BaseModel):
    start_datetime: datetime
    end_datetime: datetime
    reason: Optional[str] = None
    recurrence_rule: Optional[str] = None

class BlockedSlotCreate(BlockedSlotBase):
    pass

class BlockedSlotOut(BlockedSlotBase):
    id: str
    specialist_id: str
