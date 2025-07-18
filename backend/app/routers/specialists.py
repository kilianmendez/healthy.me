from fastapi import APIRouter, HTTPException, status, Depends
from schemas.specialist import Specialist, SpecialistCreate, SpecialistOut
from db.models.user import individual_serial, list_serial
from db.client import collection_name
from bson import ObjectId
from typing import List
from datetime import datetime, date
import os

router = APIRouter()

# ----------Functions-----------
def convert_dates_to_datetime(data):
    from datetime import datetime, date
    if isinstance(data, dict):
        return {k: convert_dates_to_datetime(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_dates_to_datetime(item) for item in data]
    elif isinstance(data, date) and not isinstance(data, datetime):
        return datetime.combine(data, datetime.min.time())
    else:
        return data
# -------------------------------

# ---------------Specialist----------------

@router.post("/", response_model=Specialist, status_code=status.HTTP_201_CREATED)
async def create_specialist(specialist: SpecialistCreate):
    """
    Create a new specialist.
    """
    specialist_dict = specialist.dict()
    specialist_dict["created_at"] = datetime.combine(date.today(), datetime.min.time())
    specialist_dict = convert_dates_to_datetime(specialist_dict)
    specialist_dict["_id"] = ObjectId()
    collection_name.insert_one(specialist_dict)
    specialist_dict["id"] = str(specialist_dict["_id"])
    return Specialist(**specialist_dict)

@router.get("/specialist_id}", response_model=SpecialistOut)
async def get_specialist(specialist_id: str):
    """
    Retrieve a specific specialist by ID.
    """
    specialist = collection_name.find_one({"_id": ObjectId(specialist_id), "role": "specialist"})
    if not specialist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Specialist not found")
    return individual_serial(specialist)

@router.get("/", response_model=List[SpecialistOut])
async def get_specialists():
    """
    Retrieve a list of all specialists.
    """
    specialists = collection_name.find({"role": "specialist"})
    return list_serial(specialists)

