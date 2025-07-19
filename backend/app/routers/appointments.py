from fastapi import APIRouter, HTTPException, status
from schemas.appointment import Appointment, AppointmentOut, AppointmentUpdate
from db.client import appointments_collection
from bson import ObjectId
from typing import List
from datetime import datetime, date

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
# -------------------------------

# ----------Endpoints-----------
@router.post("/", response_model=AppointmentOut, status_code=status.HTTP_201_CREATED)
async def create_appointment(appointment: Appointment):
    """Create a new appointment."""
    appointment_data = appointment.dict()
    appointment_data = convert_dates_to_datetime(appointment_data)

    result = appointments_collection.insert_one(appointment_data)
    if not result.acknowledged:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create appointment")

    created_appointment = appointments_collection.find_one({"_id": result.inserted_id})
    return AppointmentOut(id=str(created_appointment["_id"]), **created_appointment)


@router.get("/", response_model=List[AppointmentOut])
async def list_appointments(skip: int = 0, limit: int = 10):
    """List all appointments with pagination."""
    appointments = appointments_collection.find().skip(skip).limit(limit)
    return [AppointmentOut(id=str(a["_id"]), **a) for a in appointments]


@router.get("/{appointment_id}", response_model=AppointmentOut)
async def get_appointment(appointment_id: str):
    """Get a specific appointment by ID."""
    appointment = appointments_collection.find_one({"_id": ObjectId(appointment_id)})
    if not appointment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")
    return AppointmentOut(id=str(appointment["_id"]), **appointment)


@router.put("/{appointment_id}", response_model=AppointmentOut)
async def update_appointment(appointment_id: str, appointment_update: AppointmentUpdate):
    """Update an existing appointment."""
    update_data = appointment_update.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()
    update_data = convert_dates_to_datetime(update_data)

    result = appointments_collection.find_one_and_update(
        {"_id": ObjectId(appointment_id)},
        {"$set": update_data},
        return_document=True
    )

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")

    result["id"] = str(result["_id"])
    return AppointmentOut(**result)


@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_appointment(appointment_id: str):
    """Delete an appointment by ID."""
    result = appointments_collection.delete_one({"_id": ObjectId(appointment_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")
    return {"message": "Appointment deleted successfully"}
# -------------------------------

