from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
from bson import ObjectId
from datetime import datetime, date

from db.client import prescriptions_collection
from db.models.prescription import individual_serial, list_serial
from schemas.prescription import Prescription
from .auth import get_current_user

router = APIRouter()

# Access control: Only specialists can create/update/delete
def only_specialists(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "specialist":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only specialists can perform this action"
        )
    return current_user

# ----------- Endpoints ------------

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_prescription(prescription: Prescription, current_user: dict = Depends(only_specialists)):
    """Create a new prescription."""
    prescription_data = prescription.dict()
    
    # Add creation timestamp
    prescription_data["created_at"] = datetime.utcnow()
    
    result = prescriptions_collection.insert_one(prescription_data)
    if not result.acknowledged:
        raise HTTPException(status_code=500, detail="Failed to create prescription")
    
    created = prescriptions_collection.find_one({"_id": result.inserted_id})
    return individual_serial(created)


@router.get("/", response_model=List[dict])
async def list_prescriptions(skip: int = 0, limit: int = 10):
    """List all prescriptions."""
    prescriptions = prescriptions_collection.find().skip(skip).limit(limit)
    return list_serial(prescriptions)


@router.get("/{prescription_id}", response_model=dict)
async def get_prescription(prescription_id: str):
    """Get a single prescription by its ID."""
    prescription = prescriptions_collection.find_one({"_id": ObjectId(prescription_id)})
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    return individual_serial(prescription)


@router.put("/{prescription_id}", response_model=dict)
async def update_prescription(prescription_id: str, updated: Prescription, current_user: dict = Depends(only_specialists)):
    """Update a prescription."""
    updated_data = updated.dict()
    updated_data["updated_at"] = datetime.utcnow()

    result = prescriptions_collection.find_one_and_update(
        {"_id": ObjectId(prescription_id)},
        {"$set": updated_data},
        return_document=True
    )

    if not result:
        raise HTTPException(status_code=404, detail="Prescription not found")
    return individual_serial(result)


@router.delete("/{prescription_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_prescription(prescription_id: str, current_user: dict = Depends(only_specialists)):
    """Delete a prescription by its ID."""
    result = prescriptions_collection.delete_one({"_id": ObjectId(prescription_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Prescription not found")
    return {"message": "Prescription deleted successfully"}

@router.get("/by-patient/{patient_id}", response_model=List[dict])
async def get_prescriptions_by_patient(patient_id: str):
    """Get all prescriptions prescribed to a specific patient."""
    prescriptions = prescriptions_collection.find({"prescribed_to": patient_id})
    return list_serial(prescriptions)

@router.get("/by-specialist/{specialist_id}", response_model=List[dict])
async def get_prescriptions_by_specialist(specialist_id: str):
    """Get all prescriptions created by a specific specialist."""
    prescriptions = prescriptions_collection.find({"prescribed_by": specialist_id})
    return list_serial(prescriptions)
