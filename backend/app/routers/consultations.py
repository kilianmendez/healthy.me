from fastapi import APIRouter, HTTPException, status, Depends
from schemas.consultation import Consultation, ConsultationOut, ConsultationUpdate
from db.client import consultations_collection
from bson import ObjectId
from typing import List
from datetime import datetime, date
from .auth import get_current_user
from datetime import datetime, date, timedelta
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
    consultation_data = consultation.dict()
    consultation_data = convert_dates_to_datetime(consultation_data)

    result = consultations_collection.insert_one(consultation_data)
    if not result.acknowledged:
        raise HTTPException(status_code=500, detail="Failed to create consultation")

    created = consultations_collection.find_one({"_id": result.inserted_id})
    return ConsultationOut(id=str(created["_id"]), **created)

from fastapi import Query

@router.get("/search", response_model=List[ConsultationOut])
async def search_consultations(
    diagnosis: Optional[str] = Query(None, description="Partial diagnosis to search"),
    reason: Optional[str] = Query(None, description="Partial reason to search"),
    notes: Optional[str] = Query(None, description="Partial notes to search"),
    specialist_id: Optional[str] = Query(None, description="Filter by specialist id"),
    patient_id: Optional[str] = Query(None, description="Filter by patient id"),
    date_from: Optional[date] = Query(None, description="Filter from date"),
    date_to: Optional[date] = Query(None, description="Filter to date"),
    skip: int = 0,
    limit: int = 10
):
    query = {}

    def make_fuzzy_regex(value: str) -> str:
        # Crea regex como .*a.*s.*m.*a.* para aproximar similitud
        return ".*" + ".*".join(value) + ".*"

    if diagnosis:
        regex = make_fuzzy_regex(diagnosis)
        query["diagnosis"] = {"$regex": regex, "$options": "i"}

    if reason:
        regex = make_fuzzy_regex(reason)
        query["reason"] = {"$regex": regex, "$options": "i"}

    if notes:
        regex = make_fuzzy_regex(notes)
        query["notes"] = {"$regex": regex, "$options": "i"}

    if specialist_id:
        query["specialist_id"] = specialist_id

    if patient_id:
        query["patient_id"] = patient_id

    if date_from or date_to:
        query["date"] = {}
        if date_from:
            query["date"]["$gte"] = date_from
        if date_to:
            query["date"]["$lte"] = date_to
        # Si no hay fechas válidas, se elimina la query vacía
        if not query["date"]:
            query.pop("date")

    consultations = consultations_collection.find(query).skip(skip).limit(limit)
    return [ConsultationOut(id=str(c["_id"]), **c) for c in consultations]


@router.get("/", response_model=List[ConsultationOut])
async def list_consultations(skip: int = 0, limit: int = 10):
    consultations = consultations_collection.find().skip(skip).limit(limit)
    return [ConsultationOut(id=str(c["_id"]), **c) for c in consultations]

@router.get("/{consultation_id}", response_model=ConsultationOut)
async def get_consultation(consultation_id: str):
    consultation = consultations_collection.find_one({"_id": ObjectId(consultation_id)})
    if not consultation:
        raise HTTPException(status_code=404, detail="Consultation not found")
    return ConsultationOut(id=str(consultation["_id"]), **consultation)

@router.put("/{consultation_id}", response_model=ConsultationOut)
async def update_consultation(consultation_id: str, consultation_update: ConsultationUpdate, current_user: dict = Depends(only_specialists)):
    update_data = consultation_update.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()
    update_data = convert_dates_to_datetime(update_data)

    updated = consultations_collection.find_one_and_update(
        {"_id": ObjectId(consultation_id)},
        {"$set": update_data},
        return_document=True
    )

    if not updated:
        raise HTTPException(status_code=404, detail="Consultation not found")
    
    return ConsultationOut(id=str(updated["_id"]), **updated)

@router.delete("/{consultation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_consultation(consultation_id: str):
    """WILL BE DELETED IN THE FUTURE."""
    result = consultations_collection.delete_one({"_id": ObjectId(consultation_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Consultation not found")
    return {"message": "Consultation deleted successfully"}


@router.get("/by-specialist/{specialist_id}", response_model=List[ConsultationOut])
async def get_consultations_by_specialist(specialist_id: str, skip: int = 0, limit: int = 10):
    """Get all consultations made by a specific specialist."""
    consultations = consultations_collection.find({"specialist_id": specialist_id}).skip(skip).limit(limit)
    return [ConsultationOut(id=str(c["_id"]), **c) for c in consultations]

@router.get("/by-patient/{patient_id}", response_model=List[ConsultationOut])
async def get_consultations_by_patient(patient_id: str, skip: int = 0, limit: int = 10):
    """Get all consultations for a specific patient."""
    consultations = consultations_collection.find({"patient_id": patient_id}).skip(skip).limit(limit)
    return [ConsultationOut(id=str(c["_id"]), **c) for c in consultations]


