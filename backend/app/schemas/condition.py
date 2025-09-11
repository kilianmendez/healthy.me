from pydantic import BaseModel
from typing import Optional

# ----------Schemas----------
class Condition(BaseModel):
    name: str
    description: Optional[str] = None

class ConditionOut(Condition):
    id: str

class ConditionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
# ---------------------------