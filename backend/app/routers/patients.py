from fastapi import APIRouter, HTTPException, status, Depends
from schemas.patient import Patient, PatientCreate, PatientOut
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

# ---------------Patient----------------
@router.post("/", response_model=PatientOut, status_code=status.HTTP_201_CREATED)
async def create_patient(patient: PatientCreate):
    """
    Create a new patient.
    """
    patient_dict = patient.dict()
    patient_dict["created_at"] = datetime.combine(date.today(), datetime.min.time())
    patient_dict = convert_dates_to_datetime(patient_dict)
    patient_dict["_id"] = ObjectId()
    collection_name.insert_one(patient_dict)
    patient_dict["id"] = str(patient_dict["_id"])
    return PatientOut(**patient_dict)

@router.get("/{patient_id}", response_model=PatientOut)
async def get_patient(patient_id: str):
    """
    Retrieve a specific patient by ID.
    """
    patient = collection_name.find_one({"_id": ObjectId(patient_id), "role": "patient"})
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    return individual_serial(patient)

@router.get("/", response_model=List[PatientOut])
async def get_patients():
    """
    Retrieve a list of all patients.
    """
    patients = collection_name.find({"role": "patient"})
    return list_serial(patients)