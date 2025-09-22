# routers/diagnoses.py
from fastapi import APIRouter, HTTPException, status, Depends
from schemas.diagnosis import DiagnosisCreate, DiagnosisOut, DiagnosisUpdate
from db.client import diagnoses_collection, users_collection
from bson import ObjectId
from typing import List, Optional
from datetime import datetime, date
from routers.auth import get_current_user

router = APIRouter()

# ----------Functions-----------

def convert_dates_to_datetime(data):
    if isinstance(data, dict):
        return {k: convert_dates_to_datetime(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_dates_to_datetime(item) for item in data]
    elif isinstance(data, date) and not isinstance(data, datetime):
        return datetime.combine(data, datetime.min.time())
    else:
        return data

def convert_datetime_to_date_fields(data: dict, date_fields: List[str]):
    for field in date_fields:
        if field in data and isinstance(data[field], datetime):
            data[field] = data[field].date()
    return data

# -------------------------------

# ----------Endpoints-----------

@router.post("/", response_model=DiagnosisOut, status_code=status.HTTP_201_CREATED)
async def create_diagnosis(diagnosis: DiagnosisCreate, current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "specialist":
        raise HTTPException(status_code=403, detail="Only specialists can create diagnoses")

    # Check if the patient is in the specialist's patient list
    specialist = users_collection.find_one({"_id": ObjectId(current_user.get("id"))})
    if diagnosis.patient_id not in specialist.get("patients", []):
        raise HTTPException(status_code=403, detail="You can only create diagnoses for your own patients")

    diagnosis_data = diagnosis.dict()
    diagnosis_data = convert_dates_to_datetime(diagnosis_data)

    result = diagnoses_collection.insert_one(diagnosis_data)
    if not result.acknowledged:
        raise HTTPException(status_code=500, detail="Failed to create diagnosis")

    created = diagnoses_collection.find_one({"_id": result.inserted_id})
    convert_datetime_to_date_fields(created, ["diagnosed_at"])

    return DiagnosisOut(id=str(created["_id"]), **created)

@router.get("/by-patient/{patient_id}", response_model=List[DiagnosisOut])
async def get_diagnoses_by_patient(patient_id: str, skip: int = 0, limit: int = 10, current_user: dict = Depends(get_current_user)):
    """Get all diagnoses for a specific patient."""
    # Check if the current user is the patient themselves
    if current_user.get("id") != patient_id and current_user.get("role") != "admin":
        # If the user is a specialist, check if they are assigned to the patient
        if current_user.get("role") == "specialist":
            specialist = users_collection.find_one({"_id": ObjectId(current_user.get("id"))})
            if patient_id not in specialist.get("patients", []):
                raise HTTPException(status_code=403, detail="You are not authorized to view these diagnoses")
        else:
            raise HTTPException(status_code=403, detail="You are not authorized to view these diagnoses")

    diagnoses = diagnoses_collection.find({"patient_id": patient_id}).skip(skip).limit(limit)
    
    result = []
    for d in diagnoses:
        convert_datetime_to_date_fields(d, ["diagnosed_at"])
        result.append(DiagnosisOut(id=str(d["_id"]), **d))
    
    return result

@router.get("/{diagnosis_id}", response_model=DiagnosisOut)
async def get_diagnosis(diagnosis_id: str, current_user: dict = Depends(get_current_user)):
    diagnosis = diagnoses_collection.find_one({"_id": ObjectId(diagnosis_id)})
    if not diagnosis:
        raise HTTPException(status_code=404, detail="Diagnosis not found")

    # Check if the current user is the patient, the specialist who created it, or an admin
    if (current_user.get("id") != diagnosis.get("patient_id") and
            current_user.get("id") != diagnosis.get("specialist_id") and
            current_user.get("role") != "admin"):
        raise HTTPException(status_code=403, detail="You are not authorized to view this diagnosis")

    convert_datetime_to_date_fields(diagnosis, ["diagnosed_at"])
    return DiagnosisOut(id=str(diagnosis["_id"]), **diagnosis)

@router.put("/{diagnosis_id}", response_model=DiagnosisOut)
async def update_diagnosis(diagnosis_id: str, diagnosis_update: DiagnosisUpdate, current_user: dict = Depends(get_current_user)):
    diagnosis = diagnoses_collection.find_one({"_id": ObjectId(diagnosis_id)})
    if not diagnosis:
        raise HTTPException(status_code=404, detail="Diagnosis not found")

    # Check if the current user is the specialist who created the diagnosis
    if current_user.get("id") != diagnosis.get("specialist_id"):
        raise HTTPException(status_code=403, detail="You are not authorized to update this diagnosis")

    update_data = diagnosis_update.dict(exclude_unset=True)
    update_data = convert_dates_to_datetime(update_data)

    updated = diagnoses_collection.find_one_and_update(
        {"_id": ObjectId(diagnosis_id)},
        {"$set": update_data},
        return_document=True
    )

    if not updated:
        raise HTTPException(status_code=404, detail="Diagnosis not found or no changes made")

    convert_datetime_to_date_fields(updated, ["diagnosed_at"])
    return DiagnosisOut(id=str(updated["_id"]), **updated)

@router.delete("/{diagnosis_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_diagnosis(diagnosis_id: str, current_user: dict = Depends(get_current_user)):
    diagnosis = diagnoses_collection.find_one({"_id": ObjectId(diagnosis_id)})
    if not diagnosis:
        raise HTTPException(status_code=404, detail="Diagnosis not found")

    # Check if the current user is the specialist who created it or an admin
    if (current_user.get("id") != diagnosis.get("specialist_id") and
            current_user.get("role") != "admin"):
        raise HTTPException(status_code=403, detail="You are not authorized to delete this diagnosis")

    result = diagnoses_collection.delete_one({"_id": ObjectId(diagnosis_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Diagnosis not found")
    return {"message": "Diagnosis deleted successfully"}
