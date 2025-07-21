from fastapi import APIRouter, HTTPException, status, Depends
from passlib.context import CryptContext
from schemas.treatment import Treatment, TreatmentOut, TreatmentUpdate
from db.models.user import individual_serial, list_serial
from db.client import treatments_collection
from bson import ObjectId
from typing import List
from datetime import datetime, date, timedelta
import os
from .auth import get_current_user

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
@router.post("/", response_model=TreatmentOut, status_code=status.HTTP_201_CREATED)
async def create_treatment(treatment: Treatment, current_user: dict = Depends(only_specialists)):
    """Create a new treatment."""
    treatment_data = treatment.dict()

    # Convert start_date
    if not treatment_data.get("start_date"):
        treatment_data["start_date"] = datetime.now()
    else:
        if isinstance(treatment_data["start_date"], date) and not isinstance(treatment_data["start_date"], datetime):
            start = treatment_data["start_date"]
            treatment_data["start_date"] = datetime(start.year, start.month, start.day)

    # Convert end_date if present
    if treatment_data.get("end_date"):
        if isinstance(treatment_data["end_date"], date) and not isinstance(treatment_data["end_date"], datetime):
            end = treatment_data["end_date"]
            treatment_data["end_date"] = datetime(end.year, end.month, end.day)

    # Set default status if not provided
    treatment_data["status"] = treatment_data.get("status", "ongoing")

    # Insert in DB
    result = treatments_collection.insert_one(treatment_data)
    if not result.acknowledged:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create treatment")

    # Fetch and return created treatment
    created_treatment = treatments_collection.find_one({"_id": result.inserted_id})
    return TreatmentOut(id=str(created_treatment["_id"]), **created_treatment)

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

# -------------------------------


