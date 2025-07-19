from fastapi import APIRouter, HTTPException, status, Depends
from schemas.patient import Patient, PatientCreate, PatientOut, PatientUpdate
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

# ---------------Endpoints----------------
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

from datetime import datetime

@router.put("/{patient_id}", response_model=PatientOut)
async def update_patient(patient_id: str, patient_update: PatientUpdate):
    """
    Update an existing patient's information.
    """
    update_data = patient_update.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow().date()
    update_data = convert_dates_to_datetime(update_data)
    
    result = collection_name.find_one_and_update(
        {"_id": ObjectId(patient_id), "role": "patient"},
        {"$set": update_data},
        return_document=True
    )
    
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    
    result["id"] = str(result["_id"])
    return PatientOut(**result)

@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_patient(patient_id: str):
    """
    Delete a patient by ID.
    """
    result = collection_name.delete_one({"_id": ObjectId(patient_id), "role": "patient"})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    return {"detail": "Patient deleted successfully"}

# -------------------------------