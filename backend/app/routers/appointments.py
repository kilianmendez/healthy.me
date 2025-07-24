from fastapi import APIRouter, HTTPException, status
from schemas.appointment import Appointment, AppointmentOut, AppointmentUpdate
from db.client import appointments_collection
from bson import ObjectId
from typing import List
from datetime import datetime, date
from fastapi import Query
from typing import Optional
from schemas.appointment import AppointmentStatus

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
    limit: int = 10
):
    query = {}

    def make_fuzzy_regex(value: str) -> str:
        # Genera patrón para búsqueda flexible: "ama" => ".*a.*m.*a.*"
        return ".*" + ".*".join(value) + ".*"

    if reason:
        regex = make_fuzzy_regex(reason)
        query["reason"] = {"$regex": regex, "$options": "i"}

    if notes:
        regex = make_fuzzy_regex(notes)
        query["notes"] = {"$regex": regex, "$options": "i"}

    if specialist_id:
        query["specialist_id"] = specialist_id

    if patient_id:
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


@router.get("/by-patient/{patient_id}", response_model=List[AppointmentOut])
async def get_appointments_by_patient(patient_id: str, skip: int = 0, limit: int = 10):
    """Get all appointments for a specific patient."""
    appointments = appointments_collection.find({"patient_id": patient_id}).skip(skip).limit(limit)
    return [AppointmentOut(id=str(a["_id"]), **a) for a in appointments]

@router.get("/by-specialist/{specialist_id}", response_model=List[AppointmentOut])
async def get_appointments_by_specialist(specialist_id: str, skip: int = 0, limit: int = 10):
    """Get all appointments for a specific specialist."""
    appointments = appointments_collection.find({"specialist_id": specialist_id}).skip(skip).limit(limit)
    return [AppointmentOut(id=str(a["_id"]), **a) for a in appointments]

# -------------------------------

