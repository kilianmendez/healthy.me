from fastapi import APIRouter, HTTPException, status, Depends, Query, Response
from schemas.patient import Patient, PatientUpdate, PatientPrivate, PatientPublic, PatientSelfUpdate
from db.models.user import individual_serial, list_serial
from utils.user_utils import convert_dates_to_datetime

from db.client import users_collection
from bson import ObjectId
from typing import List, Union
from datetime import datetime, date
from .auth import get_current_user
from passlib.context import CryptContext
from typing import Optional


router = APIRouter()


# -------------------------------

# ---------------Endpoints----------------

@router.get("/", response_model=List[PatientPublic])
async def get_patients(current_user: dict = Depends(get_current_user)):
    """
    Retrieve a list of patients.
    - Admins can see all patients.
    - Specialists can only see their assigned patients.
    """
    user_role = current_user.get("role")

    if user_role == "admin":
        query = {"role": "patient"}
    elif user_role == "specialist":
        patient_ids = [ObjectId(p_id) for p_id in current_user.get("patients", [])]
        if not patient_ids:
            return []  # Return empty list if specialist has no patients
        query = {"_id": {"$in": patient_ids}, "role": "patient"}
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to list patients"
        )

    patients = users_collection.find(query)
    result = []
    for patient in patients:
        patient["id"] = str(patient["_id"])
        result.append(PatientPublic(**patient))
    return result

@router.get("/search", response_model=List[PatientPublic])
async def search_patients(
    current_user: dict = Depends(get_current_user),
    username: Optional[str] = Query(None, description="Search by username (partial, case-insensitive)"),
    full_name: Optional[str] = Query(None, description="Search by full name (partial, case-insensitive)"),
):
    """
    Search for patients.
    - Admins can search all patients.
    - Specialists can only search their assigned patients.
    """
    user_role = current_user.get("role")
    query = {"role": "patient"}

    if user_role == "admin":
        pass  # No additional query constraints for admin
    elif user_role == "specialist":
        patient_ids = [ObjectId(p_id) for p_id in current_user.get("patients", [])]
        if not patient_ids:
            return []  # Return empty list if specialist has no patients
        query["_id"] = {"$in": patient_ids}
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to search patients"
        )

    if username:
        query["username"] = {"$regex": username, "$options": "i"}
    if full_name:
        query["full_name"] = {"$regex": full_name, "$options": "i"}

    patients = users_collection.find(query)
    result = []
    for patient in patients:
        patient["id"] = str(patient["_id"])
        result.append(PatientPublic(**patient))

    return result

@router.get("/{patient_id}", response_model=PatientPrivate)
async def get_patient(patient_id: str, current_user: dict = Depends(get_current_user)):
    """
    Retrieve a specific patient by ID.
    Returns full details only for the patient themselves, their assigned specialist, or an admin.
    """
    # Authorization Logic
    user_role = current_user.get("role")
    user_id = current_user.get("id")

    is_the_patient_themselves = user_id == patient_id
    is_admin = user_role == "admin"
    is_specialist_for_patient = user_role == "specialist" and patient_id in current_user.get("patients", [])

    if not (is_the_patient_themselves or is_admin or is_specialist_for_patient):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this patient's information."
        )

    patient = users_collection.find_one({"_id": ObjectId(patient_id), "role": "patient"})
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    # Convert dates before returning
    patient["id"] = str(patient["_id"])
    if "updated_at" in patient and isinstance(patient["updated_at"], datetime):
        patient["updated_at"] = patient["updated_at"].date()
    if "created_at" in patient and isinstance(patient["created_at"], datetime):
        patient["created_at"] = patient["created_at"].date()

    # Do not return the patient_code
    patient.pop("patient_code", None)  # Use pop to avoid KeyError if field is not present

    return PatientPrivate(**patient)

@router.put("/me", response_model=PatientPrivate, response_model_exclude_unset=True)
async def update_patient(
    patient_update: PatientSelfUpdate, 
    current_user: dict = Depends(get_current_user)
):
    """
    Update the current patient's information.
    """
    patient_id = current_user["id"]
    if current_user.get("role") != "patient":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only patients can update their own information."
        )

    update_data = patient_update.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()
    update_data = convert_dates_to_datetime(update_data)

    result = users_collection.find_one_and_update(
        {"_id": ObjectId(patient_id), "role": "patient"},
        {"$set": update_data},
        return_document=True
    )

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    result["id"] = str(result["_id"])
    if "updated_at" in result and isinstance(result["updated_at"], datetime):
        result["updated_at"] = result["updated_at"].date()
    if "created_at" in result and isinstance(result["created_at"], datetime):
        result["created_at"] = result["created_at"].date()
        
    result.pop("patient_code", None)

    return PatientPrivate(**result)

@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_patient(
    patient_id: str, 
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a patient by ID.
    Only the patient themselves or an admin can perform this action.
    """
    if current_user["role"] != "admin" and current_user["id"] != patient_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this patient"
        )

    result = users_collection.delete_one({"_id": ObjectId(patient_id), "role": "patient"})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    return Response(status_code=status.HTTP_204_NO_CONTENT)
