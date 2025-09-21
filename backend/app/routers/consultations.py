from fastapi import APIRouter, HTTPException, status, Depends
from schemas.consultation import Consultation, ConsultationOut, ConsultationOutSimple
from schemas.appointment import AppointmentStatus
from schemas.diagnosis import DiagnosisCreate, DiagnosisOut
from schemas.treatment import TreatmentOut
from db.client import consultations_collection, appointments_collection, treatments_collection, diagnoses_collection
from bson import ObjectId
from typing import List
from datetime import datetime, date
from .auth import get_current_user
from datetime import datetime, date, timedelta, timezone
from fastapi import Query
from typing import Optional


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
    
def only_specialists(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "specialist":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action"
        )
    return current_user
# -------------------------------

# ----------Endpoints-----------

@router.post("/", response_model=ConsultationOut, status_code=status.HTTP_201_CREATED)
async def create_consultation(consultation: Consultation, current_user: dict = Depends(only_specialists)):
    consultation_data = consultation.dict(exclude_unset=True)
    consultation_data["specialist_id"] = current_user["id"]

    # Handle diagnosis
    diagnosis_input = consultation_data.pop("diagnosis", None)
    diagnosis_id = None
    if diagnosis_input:
        if isinstance(diagnosis_input, dict): # It's a new diagnosis to create
            from schemas.diagnosis import DiagnosisCreate
            new_diagnosis = DiagnosisCreate(**diagnosis_input)
            new_diagnosis_data = new_diagnosis.dict()
            new_diagnosis_data["specialist_id"] = current_user["id"]
            new_diagnosis_data["patient_id"] = consultation_data.get("patient_id")
            new_diagnosis_data = convert_dates_to_datetime(new_diagnosis_data)
            result = diagnoses_collection.insert_one(new_diagnosis_data)
            diagnosis_id = str(result.inserted_id)
        elif isinstance(diagnosis_input, str): # It's an existing diagnosis ID
            diagnosis_id = diagnosis_input
    
    if diagnosis_id:
        consultation_data["diagnosis_id"] = diagnosis_id

    # Handle treatments: create them as separate documents
    if "treatments" in consultation_data and consultation_data["treatments"]:
        treatment_ids = []
        for treatment_data in consultation_data["treatments"]:
            # Assuming treatment_data is a dict that can be parsed by Treatment model
            from schemas.treatment import Treatment
            treatment = Treatment(**treatment_data)
            treatment_data_to_db = treatment.dict()
            treatment_data_to_db["prescribed_by"] = consultation_data["specialist_id"]
            treatment_data_to_db["prescribed_to"] = consultation_data.get("patient_id")
            treatment_data_to_db = convert_dates_to_datetime(treatment_data_to_db)
            result = treatments_collection.insert_one(treatment_data_to_db)
            treatment_ids.append(str(result.inserted_id))
        consultation_data["treatments"] = treatment_ids

    consultation_data = convert_dates_to_datetime(consultation_data)

    result = consultations_collection.insert_one(consultation_data)
    if not result.acknowledged:
        raise HTTPException(status_code=500, detail="Failed to create consultation")
    
    # Update appointment status to completed
    if consultation_data.get("appointment_id"):
        appointments_collection.update_one(
            {"_id": ObjectId(consultation_data["appointment_id"])},
            {"$set": {"status": AppointmentStatus.completed.value}}
        )

    created = consultations_collection.find_one({"_id": result.inserted_id})

    # Populate diagnosis and treatments before returning
    if created.get("diagnosis_id"):
        diag = diagnoses_collection.find_one({"_id": ObjectId(created["diagnosis_id"])})
        if diag:
            diag["id"] = str(diag["_id"])
            created["diagnosis"] = diag

    if created.get("treatments"):
        treatment_ids = [ObjectId(tid) for tid in created["treatments"]]
        treatments = list(treatments_collection.find({"_id": {"$in": treatment_ids}}))
        for t in treatments:
            t["id"] = str(t["_id"])
        created["treatments"] = treatments

    return ConsultationOut(id=str(created["_id"]), **created)

from fastapi import Query

def make_fuzzy_regex(value: str) -> str:
    # Crea regex como .*a.*s.*m.*a.* para aproximar similitud
    return ".*" + ".*".join(value) + ".*"

@router.get("/search", response_model=List[ConsultationOutSimple])
async def search_consultations(
    diagnosis: Optional[str] = Query(None, description="Partial diagnosis to search"),
    reason: Optional[str] = Query(None, description="Partial reason to search"),
    notes: Optional[str] = Query(None, description="Partial notes to search"),
    specialist_id: Optional[str] = Query(None, description="Filter by specialist id"),
    patient_id: Optional[str] = Query(None, description="Filter by patient id"),
    date_from: Optional[date] = Query(None, description="Filter from date"),
    date_to: Optional[date] = Query(None, description="Filter to date"),
    skip: int = 0,
    limit: int = 10,
    current_user: dict = Depends(get_current_user)
):
    query = {}
    role = current_user.get("role")
    user_id = current_user.get("id")

    # Admin can filter by specialist or patient, otherwise, filter by user_id
    if role == "admin":
        if specialist_id:
            query["specialist_id"] = specialist_id
        if patient_id:
            query["patient_id"] = patient_id
    elif role == "specialist":
        query["specialist_id"] = user_id
        if patient_id:
            query["patient_id"] = patient_id
    elif role == "patient":
        query["patient_id"] = user_id
    else:
        raise HTTPException(status_code=403, detail="You do not have permission to search consultations.")

    # For better performance, consider creating a text index on diagnosis, reason, and notes
    # and using the $text operator for searches.
    if diagnosis:
        regex = make_fuzzy_regex(diagnosis)
        query["diagnosis"] = {"$regex": regex, "$options": "i"}

    if reason:
        regex = make_fuzzy_regex(reason)
        query["reason"] = {"$regex": regex, "$options": "i"}

    if notes:
        regex = make_fuzzy_regex(notes)
        query["notes"] = {"$regex": regex, "$options": "i"}

    if date_from or date_to:
        query["date"] = {}
        if date_from:
            query["date"]["$gte"] = datetime.combine(date_from, datetime.min.time()).replace(tzinfo=timezone.utc)
        if date_to:
            query["date"]["$lte"] = datetime.combine(date_to, datetime.max.time()).replace(tzinfo=timezone.utc)
        if not query["date"]:
            query.pop("date")

    consultations = consultations_collection.find(query).sort("date", -1).skip(skip).limit(limit)
    return [ConsultationOutSimple(id=str(c["_id"]), **c) for c in consultations]


@router.get("/", response_model=List[ConsultationOutSimple])
async def list_consultations(skip: int = 0, limit: int = 10, current_user: dict = Depends(get_current_user)):
    query = {}
    role = current_user.get("role")
    user_id = current_user.get("id")

    if role == "admin":
        pass  # Admins can see all consultations
    elif role == "specialist":
        query["specialist_id"] = user_id
    elif role == "patient":
        query["patient_id"] = user_id
    else:
        # Block other roles or users with no role
        raise HTTPException(status_code=403, detail="You do not have permission to view consultations.")

    consultations = consultations_collection.find(query).skip(skip).limit(limit)
    return [ConsultationOutSimple(id=str(c["_id"]), **c) for c in consultations]

@router.get("/{consultation_id}", response_model=ConsultationOut)
async def get_consultation(consultation_id: str, current_user: dict = Depends(get_current_user)):
    consultation = consultations_collection.find_one({"_id": ObjectId(consultation_id)})
    if not consultation:
        raise HTTPException(status_code=404, detail="Consultation not found")

    role = current_user.get("role")
    user_id = current_user.get("id")

    # Check permissions
    if role == "admin":
        pass  # Admin can see any consultation
    elif role == "specialist" and consultation.get("specialist_id") == user_id:
        pass  # Specialist can see their own consultation
    elif role == "patient" and consultation.get("patient_id") == user_id:
        pass  # Patient can see their own consultation
    else:
        raise HTTPException(status_code=403, detail="You do not have permission to view this consultation.")

    # Populate diagnosis
    if consultation.get("diagnosis_id"):
        diag = diagnoses_collection.find_one({"_id": ObjectId(consultation["diagnosis_id"])})
        if diag:
            diag["id"] = str(diag["_id"])
            consultation["diagnosis"] = diag

    # Populate treatments
    if consultation.get("treatments"):
        treatment_ids = [ObjectId(tid) for tid in consultation["treatments"]]
        treatments = list(treatments_collection.find({"_id": {"$in": treatment_ids}}))
        # Convert ObjectId to str for Pydantic model
        for t in treatments:
            t["id"] = str(t["_id"])
        consultation["treatments"] = treatments

    return ConsultationOut(id=str(consultation["_id"]), **consultation)


