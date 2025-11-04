from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from bson import ObjectId
from schemas.time_off import TimeOffCreate, TimeOffOut
from db.client import time_off_collection
from db.models.time_off import individual_serial, list_serial
from routers.auth import get_current_user

router = APIRouter()

# Dependency to ensure only specialists can manage time-off
def only_specialists(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "specialist":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action"
        )
    return current_user

@router.post("/", response_model=TimeOffOut, status_code=status.HTTP_201_CREATED)
async def create_time_off(
    time_off: TimeOffCreate,
    current_user: dict = Depends(only_specialists)
):
    """Create a new time-off entry for the logged-in specialist."""
    time_off_data = time_off.dict()
    time_off_data["specialist_id"] = current_user["id"]

    if time_off_data["start_datetime"] >= time_off_data["end_datetime"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End datetime must be after start datetime."
        )

    result = time_off_collection.insert_one(time_off_data)
    created_time_off = time_off_collection.find_one({"_id": result.inserted_id})
    return individual_serial(created_time_off)

@router.get("/{specialist_id}", response_model=List[TimeOffOut])
async def get_time_off_for_specialist(
    specialist_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Retrieve all time-off entries for a specific specialist."""
    if current_user["role"] == "specialist" and specialist_id != current_user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Specialists can only view their own time-off.")
    
    time_offs = time_off_collection.find({"specialist_id": specialist_id})
    return list_serial(time_offs)

@router.delete("/{time_off_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_time_off(
    time_off_id: str,
    current_user: dict = Depends(only_specialists)
):
    """Delete a time-off entry."""
    time_off = time_off_collection.find_one({"_id": ObjectId(time_off_id)})
    if not time_off:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Time-off not found")

    if time_off["specialist_id"] != current_user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to delete this time-off")

    time_off_collection.delete_one({"_id": ObjectId(time_off_id)})
    return
