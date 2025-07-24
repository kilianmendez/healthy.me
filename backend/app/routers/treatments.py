from fastapi import APIRouter, HTTPException, status, Depends
from passlib.context import CryptContext
from schemas.treatment import Treatment, TreatmentOut, TreatmentUpdate
from db.models.user import individual_serial, list_serial
from db.client import treatments_collection, prescriptions_collection
from bson import ObjectId
from typing import List
from datetime import datetime, date, timedelta
import os
from .auth import get_current_user
from fastapi import Query
from typing import Optional, List
from schemas.treatment import TreatmentStatus


router = APIRouter()

# ----------Functions-----------
def convert_dates_to_datetime(data):
    """
    Recursively convert date fields in dict/list to datetime.datetime
    """
    if isinstance(data, dict):
        new_data = {}
        for k, v in data.items():
            if isinstance(v, date) and not isinstance(v, datetime):
                new_data[k] = datetime.combine(v, datetime.min.time())
            elif isinstance(v, (dict, list)):
                new_data[k] = convert_dates_to_datetime(v)
            else:
                new_data[k] = v
        return new_data
    elif isinstance(data, list):
        return [convert_dates_to_datetime(item) for item in data]
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
@router.post("/", response_model=TreatmentOut, status_code=status.HTTP_201_CREATED)
async def create_treatment(treatment: Treatment):
    """Create a new treatment."""
    treatment_data = treatment.dict()

    # Convert all date fields in the treatment data (including nested prescriptions)
    treatment_data = convert_dates_to_datetime(treatment_data)

    prescriptions_data = treatment_data.pop("prescriptions", [])
    prescription_ids = []

    for presc in prescriptions_data:
        result_prescription = prescriptions_collection.insert_one(presc)
        if not result_prescription.acknowledged:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create prescription")
        prescription_ids.append(str(result_prescription.inserted_id))

    # Store references in the treatment
    if prescription_ids:
        treatment_data["prescription_ids"] = prescription_ids

    # Convert start_date to datetime if not already
    if not treatment_data.get("start_date"):
        treatment_data["start_date"] = datetime.now()
    else:
        if isinstance(treatment_data["start_date"], date) and not isinstance(treatment_data["start_date"], datetime):
            start = treatment_data["start_date"]
            treatment_data["start_date"] = datetime(start.year, start.month, start.day)

    # Convert end_date to datetime if present and not already
    if treatment_data.get("end_date"):
        if isinstance(treatment_data["end_date"], date) and not isinstance(treatment_data["end_date"], datetime):
            end = treatment_data["end_date"]
            treatment_data["end_date"] = datetime(end.year, end.month, end.day)

    # Set default status if not provided
    treatment_data["status"] = treatment_data.get("status", "ongoing")

    # Insert the treatment document into the treatments collection
    result = treatments_collection.insert_one(treatment_data)
    if not result.acknowledged:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create treatment")

    # Retrieve and return the created treatment
    created_treatment = treatments_collection.find_one({"_id": result.inserted_id})
    return TreatmentOut(id=str(created_treatment["_id"]), **created_treatment)



@router.get("/search/", response_model=List[TreatmentOut])
async def search_treatments(
    name: Optional[str] = Query(None, description="Search in treatment name (regex, case insensitive)"),
    description: Optional[str] = Query(None, description="Search in description (regex, case insensitive)"),
    type: Optional[str] = Query(None, description="Type of treatment (exact match or regex)"),
    prescribed_by: Optional[str] = Query(None, description="ID of specialist who prescribed"),
    prescribed_to: Optional[str] = Query(None, description="ID of patient"),
    status: Optional[TreatmentStatus] = Query(None, description="Treatment status"),
    start_date_from: Optional[date] = Query(None, description="Filter treatments starting from this date"),
    start_date_to: Optional[date] = Query(None, description="Filter treatments starting up to this date"),
    end_date_from: Optional[date] = Query(None, description="Filter treatments ending from this date"),
    end_date_to: Optional[date] = Query(None, description="Filter treatments ending up to this date"),
    skip: int = 0,
    limit: int = 10
):
    """Search treatments with multiple filters."""
    query = {}

    if name:
        query["name"] = {"$regex": name, "$options": "i"}
    if description:
        query["description"] = {"$regex": description, "$options": "i"}
    if type:
        query["type"] = {"$regex": type, "$options": "i"}
    if prescribed_by:
        query["prescribed_by"] = prescribed_by
    if prescribed_to:
        query["prescribed_to"] = prescribed_to
    if status:
        query["status"] = status.value

    if start_date_from or start_date_to:
        start_filter = {}
        if start_date_from:
            start_filter["$gte"] = datetime.combine(start_date_from, datetime.min.time())
        if start_date_to:
            start_filter["$lte"] = datetime.combine(start_date_to, datetime.max.time())
        query["start_date"] = start_filter

    if end_date_from or end_date_to:
        end_filter = {}
        if end_date_from:
            end_filter["$gte"] = datetime.combine(end_date_from, datetime.min.time())
        if end_date_to:
            end_filter["$lte"] = datetime.combine(end_date_to, datetime.max.time())
        query["end_date"] = end_filter

    treatments = treatments_collection.find(query).skip(skip).limit(limit)
    return [TreatmentOut(id=str(t["_id"]), **t) for t in treatments]

@router.get("/", response_model=List[TreatmentOut])
async def list_treatments(skip: int = 0, limit: int = 10):
    """List all treatments with pagination."""
    treatments = treatments_collection.find().skip(skip).limit(limit)
    return [TreatmentOut(id=str(t["_id"]), **t) for t in treatments]

@router.get("/{treatment_id}", response_model=TreatmentOut)
async def get_treatment(treatment_id: str):
    """Retrieve a treatment by its ID."""
    treatment = treatments_collection.find_one({"_id": ObjectId(treatment_id)})
    if not treatment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Treatment not found")
    return TreatmentOut(id=str(treatment["_id"]), **treatment)

@router.put("/{treatment_id}", response_model=TreatmentOut)
async def update_treatment(treatment_id: str, treatment_update: TreatmentUpdate, current_user: dict = Depends(only_specialists)):
    """Update an existing treatment's information."""
    update_data = treatment_update.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()
    update_data = convert_dates_to_datetime(update_data)

    result = treatments_collection.find_one_and_update(
        {"_id": ObjectId(treatment_id)},
        {"$set": update_data},
        return_document=True
    )

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Treatment not found")

    result["id"] = str(result["_id"])
    return TreatmentOut(**result)

@router.delete("/{treatment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_treatment(treatment_id: str, current_user: dict = Depends(only_specialists)):
    """Delete a treatment by its ID."""
    result = treatments_collection.delete_one({"_id": ObjectId(treatment_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Treatment not found")
    return {"message": "Treatment deleted successfully"}


@router.get("/by-patient/{user_id}", response_model=List[TreatmentOut])
async def get_treatments_by_patient(user_id: str, skip: int = 0, limit: int = 10):
    """Get all treatments assigned to a specific user (patient)."""
    treatments = treatments_collection.find({"prescribed_to": user_id}).skip(skip).limit(limit)
    return [TreatmentOut(id=str(t["_id"]), **t) for t in treatments]

@router.get("/by-specialist/{specialist_id}", response_model=List[TreatmentOut])
async def get_treatments_by_specialist(specialist_id: str, skip: int = 0, limit: int = 10):
    """Get all treatments created by a specific specialist."""
    treatments = treatments_collection.find({"prescribed_by": specialist_id}).skip(skip).limit(limit)
    return [TreatmentOut(id=str(t["_id"]), **t) for t in treatments]


# -------------------------------


