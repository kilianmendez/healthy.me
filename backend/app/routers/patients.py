from fastapi import APIRouter, HTTPException, status, Depends, Query, Response
from schemas.patient import Patient, PatientCreate, PatientUpdate, PatientPrivate, PatientPublic
from db.models.user import individual_serial, list_serial
from utils.security import validate_password_strength
from db.client import users_collection
from bson import ObjectId
from typing import List, Union
from datetime import datetime, date
from .auth import get_current_user
from passlib.context import CryptContext
from typing import Optional
import secrets

router = APIRouter()
crypt = CryptContext(schemes=["bcrypt"])

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

def generate_unique_patient_code():
    """Generates a unique 8-character hexadecimal code."""
    while True:
        code = secrets.token_hex(4).upper()
        if users_collection.find_one({"patient_code": code}) is None:
            return code
# -------------------------------

# ---------------Endpoints----------------

@router.post("/", response_model=PatientPrivate, status_code=status.HTTP_201_CREATED)
async def create_patient(patient: PatientCreate):
    """
    Create a new patient.
    """
    existing_user = users_collection.find_one({"email": patient.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists"
        )
    
    validate_password_strength(patient.password)

    patient_dict = patient.dict()
    patient_dict["patient_code"] = generate_unique_patient_code()
    patient_dict["_id"] = ObjectId()
    patient_dict["created_at"] = datetime.combine(date.today(), datetime.min.time())
    patient_dict["password"] = crypt.hash(patient_dict["password"])
    patient_dict = convert_dates_to_datetime(patient_dict)
    users_collection.insert_one(patient_dict)
    patient_dict["id"] = str(patient_dict["_id"])
    return PatientPrivate(**patient_dict)

@router.get("/search", response_model=List[PatientPublic])
async def search_patients(
    current_user: dict = Depends(get_current_user),
    username: Optional[str] = Query(None, description="Search by username (partial, case-insensitive)"),
    full_name: Optional[str] = Query(None, description="Search by full name (partial, case-insensitive)"),
):
    """Search for patients. Admin only."""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to search patients")

    query = {"role": "patient"}

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

    return PatientPrivate(**patient)

@router.get("/", response_model=List[PatientPublic])
async def get_patients(current_user: dict = Depends(get_current_user)):
    """Retrieve a list of all patients. Admin only."""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to list patients")

    patients = users_collection.find({"role": "patient"})
    result = []
    for patient in patients:
        patient["id"] = str(patient["_id"])
        result.append(PatientPublic(**patient))
    return result

@router.put("/{patient_id}", response_model=PatientPrivate)
async def update_patient(
    patient_id: str, 
    patient_update: PatientUpdate, 
    current_user: dict = Depends(get_current_user)
):
    """
    Update an existing patient's information.
    Only the patient themselves can update their profile.
    """
    if patient_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this patient"
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
