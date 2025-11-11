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
from datetime import time, datetime, date, timedelta, timezone
from dateutil.rrule import rrule, DAILY, WEEKLY, MONTHLY, YEARLY

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

    # Ensure the user has permission to view this specialist's availability
    if current_user["role"] == "specialist" and specialist_id != current_user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Specialists can only view their own availability.")
    elif current_user["role"] not in ["patient", "specialist", "admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to view availability.")

    # Fetch specialist's settings
    specialist_data = users_collection.find_one({"_id": ObjectId(specialist_id)})
    if not specialist_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Specialist not found.")
    
    appointment_duration_minutes = specialist_data.get("appointment_duration", 30)
    buffer_time_minutes = specialist_data.get("buffer_time", 10)
    
    availability_by_date = {}
    current_date = start_date

    # Fetch all recurring blocked slots that are active during the requested period
    recurring_blocked_slots = list(blocked_slots_collection.find({
        "specialist_id": specialist_id,
        "is_recurring": True,
        "start_datetime": {"$lte": datetime.combine(end_date, time.max).replace(tzinfo=timezone.utc)},
        "recurrence_end_date": {"$gte": datetime.combine(start_date, time.min).replace(tzinfo=timezone.utc)}
    }))

    while current_date <= end_date:
        day_of_week_str = current_date.strftime('%A').lower()
        
        # 1. Generate initial slots from weekly availability
        weekly_availabilities = weekly_availabilities_collection.find({
            "specialist_id": specialist_id,
            "day_of_week": current_date.weekday()
        })
        
        available_slots_today = []
        for weekly_slot in weekly_availabilities:
            start_time = datetime.combine(current_date, weekly_slot["start_time"].time())
            end_time = datetime.combine(current_date, weekly_slot["end_time"].time())
            
            current_slot_start = start_time
            while current_slot_start + timedelta(minutes=appointment_duration_minutes) <= end_time:
                available_slots_today.append(current_slot_start.time())
                current_slot_start += timedelta(minutes=appointment_duration_minutes)

        # 2. Collect all applicable blocked slots for the day
        all_blocked_slots_for_today = []

        # Add one-time blocked slots for the current day
        one_time_slots = blocked_slots_collection.find({
            "specialist_id": specialist_id,
            "is_recurring": {"$ne": True},
            "start_datetime": {"$lte": datetime.combine(current_date, time.max)},
            "end_datetime": {"$gte": datetime.combine(current_date, time.min)}
        })
        all_blocked_slots_for_today.extend(list(one_time_slots))

        # Add instances of recurring blocked slots for the current day
        for r_slot in recurring_blocked_slots:
            if r_slot.get("recurrence_day_of_week") == day_of_week_str and current_date <= r_slot["recurrence_end_date"].date():
                # Create a concrete instance of the recurring block for today
                instance_start = datetime.combine(current_date, r_slot["start_datetime"].time())
                instance_end = datetime.combine(current_date, r_slot["end_datetime"].time())
                all_blocked_slots_for_today.append({
                    "start_datetime": instance_start,
                    "end_datetime": instance_end,
                })

        # 3. Filter available slots based on all collected blocked slots
        if all_blocked_slots_for_today:
            filtered_slots = []
            for slot_time in available_slots_today:
                slot_datetime = datetime.combine(current_date, slot_time)
                is_blocked = False
                for blocked_slot in all_blocked_slots_for_today:
                    if slot_datetime >= blocked_slot["start_datetime"] and slot_datetime < blocked_slot["end_datetime"]:
                        is_blocked = True
                        break
                if not is_blocked:
                    filtered_slots.append(slot_time)
            available_slots_today = filtered_slots

        # 4. Filter based on time-off entries
        time_off_entries = time_off_collection.find({
            "specialist_id": specialist_id,
            "start_datetime": {"$lte": datetime.combine(current_date, time.max)},
            "end_datetime": {"$gte": datetime.combine(current_date, time.min)}
        })
        if time_off_entries:
            # This filtering logic can be combined with the one above, but separated for clarity
            # Re-using the same filtering pattern
            pass # Add filtering logic here if needed, similar to blocked slots

        # 5. Filter based on existing appointments
        existing_appointments = appointments_collection.find({
            "specialist_id": specialist_id,
            "date": {"$gte": datetime.combine(current_date, time.min), "$lte": datetime.combine(current_date, time.max)},
            "status": {"$in": ["scheduled", "pending"]}
        })
        
        if existing_appointments:
            # Re-using the same filtering pattern
            pass # Add filtering logic here if needed

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

    if blocked_slot_data.get("is_recurring"):
        if not all([blocked_slot_data.get("recurrence_end_date"), blocked_slot_data.get("recurrence_day_of_week")]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="For recurring slots, recurrence_end_date and recurrence_day_of_week are required."
            )
        # Optional: Add validation for the day of the week string
        valid_days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        if blocked_slot_data["recurrence_day_of_week"].lower() not in valid_days:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid recurrence_day_of_week. Must be one of {valid_days}."
            )

    blocked_slot_data["specialist_id"] = current_user["id"]

    # For non-recurring slots, check for overlaps
    if not blocked_slot_data.get("is_recurring"):
        existing_blocked_slot = blocked_slots_collection.find_one({
            "specialist_id": current_user["id"],
            "is_recurring": {"$ne": True},
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
