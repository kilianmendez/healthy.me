from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from schemas.specialist import Specialist, SpecialistOut, SpecialistUpdate, Gender, SpecialistPublicOut
from db.models.user import individual_serial, list_serial

from db.client import users_collection
from bson import ObjectId
from typing import List
from datetime import datetime, date
import os
from .auth import get_current_user
from passlib.context import CryptContext
from fastapi import Query
from typing import Optional
from fastapi.encoders import jsonable_encoder
import re

router = APIRouter()



class AddPatientByCodePayload(BaseModel):
    patient_code: str

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

@router.get("/", response_model=List[SpecialistPublicOut])
async def get_specialists():
    """
    Retrieve a list of all specialists.
    """
    specialists = users_collection.find({"role": "specialist"})
    result = []
    for specialist in specialists:
        specialist["id"] = str(specialist["_id"])
        if "updated_at" in specialist and isinstance(specialist["updated_at"], datetime):
            specialist["updated_at"] = specialist["updated_at"].date()
        result.append(SpecialistPublicOut(**specialist))
    return result

@router.get("/search/", response_model=List[SpecialistPublicOut])
async def search_specialists(
    full_name: Optional[str] = Query(None, description="Search by full name"),
    biography: Optional[str] = Query(None, description="Search in biography"),
    specialties: Optional[List[str]] = Query(None, description="One or more specialties"),
    workplaces: Optional[str] = Query(None, description="Search by workplace"),
    gender: Optional[Gender] = Query(None, description="Filter by gender"),
    min_birth_date: Optional[date] = Query(None),
    max_birth_date: Optional[date] = Query(None),
    skip: int = 0,
    limit: int = 10
):
    query = {"role": "specialist"}

    if full_name:
        query["full_name"] = {"$regex": full_name, "$options": "i"}
    if biography:
        query["biography"] = {"$regex": biography, "$options": "i"}
    if specialties:
        query["specialties"] = {
            "$elemMatch": {
                "$in": [re.compile(spec, re.IGNORECASE) for spec in specialties]
            }
        }
    if workplaces:
        query["workplaces"] = {"$elemMatch": {"$regex": workplaces, "$options": "i"}}
    if gender:
        query["gender"] = gender
    if min_birth_date or max_birth_date:
        birth_filter = {}
        if min_birth_date:
            birth_filter["$gte"] = datetime.combine(min_birth_date, datetime.min.time())
        if max_birth_date:
            birth_filter["$lte"] = datetime.combine(max_birth_date, datetime.max.time())
        query["date_of_birth"] = birth_filter

    specialists_cursor = users_collection.find(query).skip(skip).limit(limit)
    result = []

    for specialist in specialists_cursor:
        specialist["id"] = str(specialist.pop("_id"))
        if "created_at" in specialist and isinstance(specialist["created_at"], datetime):
            specialist["created_at"] = specialist["created_at"].date()
        if "updated_at" in specialist and isinstance(specialist["updated_at"], datetime):
            specialist["updated_at"] = specialist["updated_at"].date()

        result.append(SpecialistPublicOut(**specialist))

    return result


@router.get("/{specialist_id}", response_model=SpecialistPublicOut)
async def get_specialist(specialist_id: str):
    """
    Retrieve a specific specialist by ID.
    """
    specialist = users_collection.find_one({"_id": ObjectId(specialist_id), "role": "specialist"})
    if not specialist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Specialist not found")
    specialist["id"] = str(specialist["_id"])
    # Convierte updated_at a date si existe
    if "updated_at" in specialist and isinstance(specialist["updated_at"], datetime):
        specialist["updated_at"] = specialist["updated_at"].date()

    return SpecialistPublicOut(**specialist)

@router.put("/{specialist_id}", response_model=SpecialistOut)
async def update_specialist(
    specialist_id: str, 
    specialist_update: SpecialistUpdate,
    current_user: dict = Depends(get_current_user)  # Usuario autenticado
):
    # Verificar que el usuario autenticado es el mismo especialista que intenta modificar
    if specialist_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this specialist"
        )

    update_data = specialist_update.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()
    update_data = convert_dates_to_datetime(update_data)

    result = users_collection.find_one_and_update(
        {"_id": ObjectId(specialist_id), "role": "specialist"},
        {"$set": update_data},
        return_document=True
    )

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Specialist not found")

    result["id"] = str(result["_id"])
    # Convierte updated_at a date si existe
    if "updated_at" in result and isinstance(result["updated_at"], datetime):
        result["updated_at"] = result["updated_at"].date()
    return SpecialistOut(**result)

@router.post("/me/patients", response_model=SpecialistOut, status_code=status.HTTP_200_OK)
async def add_patient_by_code(
    payload: AddPatientByCodePayload,
    current_user: dict = Depends(get_current_user)
):
    """
    Adds a patient to the current specialist's list using the patient's unique code.
    """
    if current_user.get("role") != "specialist":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only specialists can add patients to their list."
        )

    specialist_id = current_user["id"]
    patient_code = payload.patient_code.upper()

    # Find the patient by their unique code
    patient = users_collection.find_one({"patient_code": patient_code, "role": "patient"})
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with code '{patient_code}' not found."
        )
    
    patient_id = str(patient["_id"])

    # Add the patient's ID to the specialist's 'patients' array
    result = users_collection.find_one_and_update(
        {"_id": ObjectId(specialist_id)},
        {"$addToSet": {"patients": patient_id}},
        return_document=True
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Specialist not found."
        )
    
    result["id"] = str(result["_id"])
    if "updated_at" in result and isinstance(result.get("updated_at"), datetime):
        result["updated_at"] = result["updated_at"].date()
    if "created_at" in result and isinstance(result.get("created_at"), datetime):
        result["created_at"] = result["created_at"].date()

    return SpecialistOut(**result)

@router.delete("/me/patients/{patient_id}", response_model=SpecialistOut, status_code=status.HTTP_200_OK)
async def remove_patient_from_specialist(
    patient_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Removes a patient from the current specialist's patient list.
    """
    if current_user.get("role") != "specialist":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only specialists can modify their patient list."
        )

    specialist_id = current_user["id"]

    if patient_id not in current_user.get("patients", []):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} is not in your patient list."
        )

    result = users_collection.find_one_and_update(
        {"_id": ObjectId(specialist_id)},
        {"$pull": {"patients": patient_id}},
        return_document=True
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Specialist not found."
        )
    
    result["id"] = str(result["_id"])
    if "updated_at" in result and isinstance(result.get("updated_at"), datetime):
        result["updated_at"] = result["updated_at"].date()
    if "created_at" in result and isinstance(result.get("created_at"), datetime):
        result["created_at"] = result["created_at"].date()

    return SpecialistOut(**result)

@router.delete("/{specialist_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_specialist(
    specialist_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a specialist by ID.
    Only the specialist themselves or an admin can perform this action.
    """
    if current_user["role"] != "admin" and current_user["id"] != specialist_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this specialist"
        )

    result = users_collection.delete_one({"_id": ObjectId(specialist_id), "role": "specialist"})

    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Specialist not found")

    return {"message": "Specialist deleted successfully"}


# -------------------------------
