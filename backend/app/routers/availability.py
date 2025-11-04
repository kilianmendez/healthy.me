from fastapi import APIRouter, HTTPException, status, Depends
from schemas.availability import (
    WeeklyAvailabilityCreate, 
    WeeklyAvailabilityOut, 
    BlockedSlotCreate, 
    BlockedSlotOut,
    WeeklyAvailabilityCreateList,
    WeeklyAvailabilityOutList
)
from db.client import weekly_availabilities_collection, blocked_slots_collection, appointments_collection, users_collection, time_off_collection
from db.models.availability import (
    individual_weekly_availability_serial, 
    list_weekly_availability_serial, 
    individual_blocked_slot_serial, 
    list_blocked_slot_serial
)
from bson import ObjectId
from typing import List, Optional, Dict
from fastapi import Query
from routers.auth import get_current_user
from datetime import time, datetime, date, timedelta

router = APIRouter()



# Dependency to ensure only specialists can manage availability
def only_specialists(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "specialist":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action"
        )
    return current_user

# --- Weekly Availability Endpoints ---

@router.post("/weekly/bulk", response_model=WeeklyAvailabilityOutList, status_code=status.HTTP_201_CREATED)
async def create_bulk_weekly_availability(
    availabilities: WeeklyAvailabilityCreateList,
    current_user: dict = Depends(only_specialists)
):
    """Create multiple weekly availability slots for the logged-in specialist."""
    # Delete all existing weekly availabilities for the specialist
    weekly_availabilities_collection.delete_many({"specialist_id": current_user["id"]})

    created_availabilities = []
    dummy_date = date.min
    for availability in availabilities.availabilities:
        availability_data = availability.dict()
        availability_data["specialist_id"] = current_user["id"]
        
        start_time = datetime.combine(dummy_date, availability_data["start_time"])
        end_time = datetime.combine(dummy_date, availability_data["end_time"])

        # Check for overlapping weekly availability for the same day
        existing_availability = weekly_availabilities_collection.find_one({
            "specialist_id": current_user["id"],
            "day_of_week": availability_data["day_of_week"],
            "$or": [
                {"$and": [
                    {"start_time": {"$lt": end_time}},
                    {"end_time": {"$gt": start_time}}
                ]},
                {"start_time": start_time},
                {"end_time": end_time}
            ]
        })

        if existing_availability:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Overlapping weekly availability already exists for day {availability_data['day_of_week']}."
            )
        
        availability_data["start_time"] = start_time
        availability_data["end_time"] = end_time

        result = weekly_availabilities_collection.insert_one(availability_data)
        created_availability = weekly_availabilities_collection.find_one({"_id": result.inserted_id})
        created_availabilities.append(individual_weekly_availability_serial(created_availability))
    return {"availabilities": created_availabilities}



@router.get("/weekly/{specialist_id}", response_model=List[WeeklyAvailabilityOut])
async def get_weekly_availability(specialist_id: str, current_user: dict = Depends(get_current_user)):
    """Retrieve all weekly availability slots for a specific specialist."""
    if current_user["role"] == "specialist":
        if specialist_id != current_user["id"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Specialists can only view their own availability.")
        id_to_query = current_user["id"]
    elif current_user["role"] == "patient" or current_user["role"] == "admin":
        id_to_query = specialist_id
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to perform this action")

    availabilities = weekly_availabilities_collection.find({"specialist_id": id_to_query})
    return list_weekly_availability_serial(availabilities)

@router.delete("/weekly/{availability_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_weekly_availability(
    availability_id: str,
    current_user: dict = Depends(only_specialists)
):
    """Delete a weekly availability slot."""
    availability = weekly_availabilities_collection.find_one({"_id": ObjectId(availability_id)})
    if not availability:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Weekly availability not found")

    if availability["specialist_id"] != current_user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to delete this availability")

    weekly_availabilities_collection.delete_one({"_id": ObjectId(availability_id)})
    return

@router.get("/slots/{specialist_id}", response_model=Dict[date, List[time]])
async def get_available_slots(
    specialist_id: str,
    start_date: date = Query(..., description="Start date to check availability for (YYYY-MM-DD)"),
        end_date: Optional[date] = Query(None, description="End date to check availability for (YYYY-MM-DD)"),
    current_user: dict = Depends(get_current_user)
):
    """
    Retrieve available time slots for a specific specialist over a date range.
    Considers weekly availability, blocked slots, and existing appointments.
    """
    if not end_date:
        end_date = start_date

    if start_date > end_date:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Start date cannot be after end date.")

    # Ensure the user has permission to view this specialist\'s availability
    if current_user["role"] == "specialist" and specialist_id != current_user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Specialists can only view their own availability.")
    elif current_user["role"] not in ["patient", "specialist", "admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to view availability.")

    # Fetch specialist's appointment duration, with a fallback to 30 minutes
    specialist_data = users_collection.find_one({"_id": ObjectId(specialist_id)})
    if not specialist_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Specialist not found.")
    
    appointment_duration_minutes = specialist_data.get("appointment_duration", 30)
    buffer_time_minutes = specialist_data.get("buffer_time", 10)
    availability_by_date = {}
    current_date = start_date

    while current_date <= end_date:
        day_of_week = current_date.weekday() # Monday is 0, Sunday is 6

        # 1. Get weekly availability for the day
        weekly_availabilities = weekly_availabilities_collection.find({
            "specialist_id": specialist_id,
            "day_of_week": day_of_week
        })
        
        available_slots_today = []
        for weekly_slot in weekly_availabilities:
            start_time = datetime.combine(current_date, weekly_slot["start_time"].time())
            end_time = datetime.combine(current_date, weekly_slot["end_time"].time())
            
            current_slot_start = start_time
            while current_slot_start + timedelta(minutes=appointment_duration_minutes) <= end_time:
                available_slots_today.append(current_slot_start.time())
                current_slot_start += timedelta(minutes=appointment_duration_minutes)

        # 2. Get blocked slots for the date
        blocked_slots = list(blocked_slots_collection.find({
            "specialist_id": specialist_id,
            "start_datetime": {"$lte": datetime.combine(current_date, time.max)},
            "end_datetime": {"$gte": datetime.combine(current_date, time.min)}
        }))

        if blocked_slots:
            filtered_slots = []
            for slot_time in available_slots_today:
                slot_datetime = datetime.combine(current_date, slot_time)
                is_blocked = False
                for blocked_slot in blocked_slots:
                    blocked_start = blocked_slot["start_datetime"]
                    blocked_end = blocked_slot["end_datetime"]
                    if slot_datetime >= blocked_start and slot_datetime < blocked_end:
                        is_blocked = True
                        break
                if not is_blocked:
                    filtered_slots.append(slot_time)
            available_slots_today = filtered_slots


        # 3. Get time-off entries for the date
        time_off_entries = list(time_off_collection.find({
            "specialist_id": specialist_id,
            "start_datetime": {"$lte": datetime.combine(current_date, time.max)},
            "end_datetime": {"$gte": datetime.combine(current_date, time.min)}
        }))

        if time_off_entries:
            filtered_slots = []
            for slot_time in available_slots_today:
                slot_datetime = datetime.combine(current_date, slot_time)
                is_time_off = False
                for time_off_entry in time_off_entries:
                    time_off_start = time_off_entry["start_datetime"]
                    time_off_end = time_off_entry["end_datetime"]
                    if slot_datetime >= time_off_start and slot_datetime < time_off_end:
                        is_time_off = True
                        break
                if not is_time_off:
                    filtered_slots.append(slot_time)
            available_slots_today = filtered_slots


        # 4. Get existing appointments for the date
        existing_appointments = list(appointments_collection.find({
            "specialist_id": specialist_id,
            "date": {"$gte": datetime.combine(current_date, time.min), "$lte": datetime.combine(current_date, time.max)},
            "status": {"$in": ["scheduled", "pending"]}
        }))

        if existing_appointments:
            filtered_slots = []
            for slot_time in available_slots_today:
                slot_datetime = datetime.combine(current_date, slot_time)
                is_booked = False
                for appointment in existing_appointments:
                    appointment_start = appointment["date"]
                    appointment_end = appointment_start + timedelta(minutes=appointment_duration_minutes + buffer_time_minutes)
                    if slot_datetime >= appointment_start and slot_datetime < appointment_end:
                        is_booked = True
                        break
                if not is_booked:
                    filtered_slots.append(slot_time)
            available_slots_today = filtered_slots
        
        available_slots_today.sort()
        availability_by_date[current_date] = available_slots_today
        current_date += timedelta(days=1)

    return availability_by_date

# --- Blocked Slots Endpoints ---

@router.post("/block/", response_model=BlockedSlotOut, status_code=status.HTTP_201_CREATED)
async def create_blocked_slot(
    blocked_slot: BlockedSlotCreate,
    current_user: dict = Depends(only_specialists)
):
    """Block a specific time range for the logged-in specialist."""
    blocked_slot_data = blocked_slot.dict()
    if blocked_slot_data["start_datetime"] >= blocked_slot_data["end_datetime"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End datetime must be after start datetime."
        )
    blocked_slot_data["specialist_id"] = current_user["id"]

    # Check for overlapping blocked slots
    existing_blocked_slot = blocked_slots_collection.find_one({
        "specialist_id": current_user["id"],
        "$or": [
            {"$and": [
                {"start_datetime": {"$lt": blocked_slot_data["end_datetime"]}},
                {"end_datetime": {"$gt": blocked_slot_data["start_datetime"]}}
            ]},
            {"start_datetime": blocked_slot_data["start_datetime"]},
            {"end_datetime": blocked_slot_data["end_datetime"]}
        ]
    })

    if existing_blocked_slot:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Overlapping blocked slot already exists."
        )

    result = blocked_slots_collection.insert_one(blocked_slot_data)
    created_blocked_slot = blocked_slots_collection.find_one({"_id": result.inserted_id})
    return individual_blocked_slot_serial(created_blocked_slot)

@router.get("/block/{specialist_id}", response_model=List[BlockedSlotOut])
async def get_blocked_slots(specialist_id: str, current_user: dict = Depends(get_current_user)):
    """Retrieve all blocked time slots for a specific specialist."""
    if current_user["role"] == "specialist":
        if specialist_id != current_user["id"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Specialists can only view their own blocked slots.")
        id_to_query = current_user["id"]
    elif current_user["role"] == "patient" or current_user["role"] == "admin":
        id_to_query = specialist_id
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to perform this action")

    blocked_slots = blocked_slots_collection.find({"specialist_id": id_to_query})
    return list_blocked_slot_serial(blocked_slots)

@router.delete("/block/{block_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_blocked_slot(
    block_id: str,
    current_user: dict = Depends(only_specialists)
):
    """Remove a blocked time slot."""
    blocked_slot = blocked_slots_collection.find_one({"_id": ObjectId(block_id)})
    if not blocked_slot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blocked slot not found")

    if blocked_slot["specialist_id"] != current_user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to delete this blocked slot")

    blocked_slots_collection.delete_one({"_id": ObjectId(block_id)})
    return
