from fastapi import APIRouter, HTTPException, status, Depends
from schemas.specialist import Specialist, SpecialistCreate, SpecialistOut, SpecialistUpdate
from db.models.user import individual_serial, list_serial
from utils.security import validate_password_strength
from db.client import users_collection
from bson import ObjectId
from typing import List
from datetime import datetime, date
import os
from .auth import get_current_user
from passlib.context import CryptContext

router = APIRouter()

crypt = CryptContext(schemes=["bcrypt"])

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
@router.post("/", response_model=Specialist, status_code=status.HTTP_201_CREATED)
async def create_specialist(specialist: SpecialistCreate):
    """
    Create a new specialist.
    """

    # Verify if a user with the same email already exists
    existing_user = users_collection.find_one({"email": specialist.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists"
        )
    
    validate_password_strength(specialist.password)

    specialist_dict = specialist.dict()
    specialist_dict["_id"] = ObjectId()
    specialist_dict["created_at"] = datetime.combine(date.today(), datetime.min.time())
    specialist_dict["password"] = crypt.hash(specialist_dict["password"])
    specialist_dict = convert_dates_to_datetime(specialist_dict)
    users_collection.insert_one(specialist_dict)
    specialist_dict["id"] = str(specialist_dict["_id"])
    return Specialist(**specialist_dict)

@router.get("/{specialist_id}", response_model=SpecialistOut)
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
    return SpecialistOut(**specialist)

@router.get("/", response_model=List[SpecialistOut])
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
        result.append(SpecialistOut(**specialist))
    return result

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
