from fastapi import APIRouter, HTTPException, status, Depends
from schemas.appointment import Appointment, AppointmentOut, AppointmentUpdate
from db.client import appointments_collection
from bson import ObjectId
from typing import List
from datetime import datetime, date
from fastapi import Query
from typing import Optional
from schemas.appointment import AppointmentStatus
from routers.auth import get_current_user

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
@router.post("/", response_model=AppointmentOut, status_code=status.HTTP_201_CREATED)
async def create_appointment(appointment: Appointment, current_user: dict = Depends(only_specialists)):
    """Create a new appointment."""
    appointment_data = appointment.dict()
    appointment_data["specialist_id"] = current_user["id"]
    appointment_data = convert_dates_to_datetime(appointment_data)

    result = appointments_collection.insert_one(appointment_data)
    if not result.acknowledged:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create appointment")

    created_appointment = appointments_collection.find_one({"_id": result.inserted_id})
    return AppointmentOut(id=str(created_appointment["_id"]), **created_appointment)

@router.get("/search", response_model=List[AppointmentOut])
async def search_appointments(
    reason: Optional[str] = Query(None, description="Partial reason to search"),
    notes: Optional[str] = Query(None, description="Partial notes to search"),
    specialist_id: Optional[str] = Query(None, description="Filter by specialist id"),
    patient_id: Optional[str] = Query(None, description="Filter by patient id"),
    status: Optional[AppointmentStatus] = Query(None, description="Filter by appointment status"),
    date_from: Optional[datetime] = Query(None, description="Filter from date"),
    date_to: Optional[datetime] = Query(None, description="Filter to date"),
    skip: int = 0,
    limit: int = 10,
    current_user: dict = Depends(get_current_user)
):
    query = {}
    role = current_user.get("role")
    user_id = current_user.get("id")

    if role == "admin":
        pass  # Admins can search all appointments
    elif role == "specialist":
        query["specialist_id"] = user_id
    elif role == "patient":
        query["patient_id"] = user_id
    else:
        raise HTTPException(status_code=403, detail="You do not have permission to search appointments.")

    def make_fuzzy_regex(value: str) -> str:
        # Genera patrón para búsqueda flexible: "ama" => ".*a.*m.*a.*"
        return ".*" + ".*".join(value) + ".*"

    if reason:
        regex = make_fuzzy_regex(reason)
        query["reason"] = {"$regex": regex, "$options": "i"}

    if notes:
        regex = make_fuzzy_regex(notes)
        query["notes"] = {"$regex": regex, "$options": "i"}

    if specialist_id and role == "admin":
        query["specialist_id"] = specialist_id

    if patient_id and role == "admin":
        query["patient_id"] = patient_id

    if status:
        query["status"] = status.value

    if date_from or date_to:
        query["date"] = {}
        if date_from:
            query["date"]["$gte"] = date_from
        if date_to:
            query["date"]["$lte"] = date_to
        if not query["date"]:
            query.pop("date")

    appointments = appointments_collection.find(query).skip(skip).limit(limit)
    return [AppointmentOut(id=str(a["_id"]), **a) for a in appointments]

@router.get("/", response_model=List[AppointmentOut])
async def list_appointments(skip: int = 0, limit: int = 10, current_user: dict = Depends(get_current_user)):
    """List all appointments with pagination."""
    query = {}
    role = current_user.get("role")
    user_id = current_user.get("id")

    if role == "admin":
        pass  # Admins can see all appointments
    elif role == "specialist":
        query["specialist_id"] = user_id
    elif role == "patient":
        query["patient_id"] = user_id
    else:
        # Block other roles or users with no role
        raise HTTPException(status_code=403, detail="You do not have permission to view appointments.")

    appointments = appointments_collection.find(query).skip(skip).limit(limit)
    return [AppointmentOut(id=str(a["_id"]), **a) for a in appointments]


@router.get("/{appointment_id}", response_model=AppointmentOut)
async def get_appointment(appointment_id: str, current_user: dict = Depends(get_current_user)):
    """Get a specific appointment by ID."""
    appointment = appointments_collection.find_one({"_id": ObjectId(appointment_id)})
    if not appointment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")

    role = current_user.get("role")
    user_id = current_user.get("id")

    # Check permissions
    if role == "admin":
        pass  # Admin can see any appointment
    elif role == "specialist" and appointment.get("specialist_id") == user_id:
        pass  # Specialist can see their own appointment
    elif role == "patient" and appointment.get("patient_id") == user_id:
        pass  # Patient can see their own appointment
    else:
        raise HTTPException(status_code=403, detail="You do not have permission to view this appointment.")

    return AppointmentOut(id=str(appointment["_id"]), **appointment)


@router.put("/{appointment_id}", response_model=AppointmentOut)
async def update_appointment(appointment_id: str, appointment_update: AppointmentUpdate, current_user: dict = Depends(get_current_user)):
    """Update an existing appointment."""
    appointment = appointments_collection.find_one({"_id": ObjectId(appointment_id)})
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    # Check if the user is the specialist who created the appointment
    if current_user.get("role") != "specialist" or appointment.get("specialist_id") != current_user.get("id"):
        raise HTTPException(status_code=403, detail="You do not have permission to update this appointment.")

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
async def delete_appointment(appointment_id: str, current_user: dict = Depends(get_current_user)):
    """Delete an appointment by ID."""
    appointment = appointments_collection.find_one({"_id": ObjectId(appointment_id)})
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    role = current_user.get("role")
    user_id = current_user.get("id")

    # Check permissions
    if role == "admin":
        pass  # Admin can delete any appointment
    elif role == "specialist" and appointment.get("specialist_id") == user_id:
        pass  # Specialist can delete their own appointment
    else:
        raise HTTPException(status_code=403, detail="You do not have permission to delete this appointment.")

    result = appointments_collection.delete_one({"_id": ObjectId(appointment_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")
    return {"message": "Appointment deleted successfully"}