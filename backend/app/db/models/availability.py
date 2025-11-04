from datetime import datetime

def individual_weekly_availability_serial(availability) -> dict:
    return {
        "id": str(availability["_id"]),
        "specialist_id": availability["specialist_id"],
        "day_of_week": availability["day_of_week"],
        "start_time": availability["start_time"].time().isoformat(),
        "end_time": availability["end_time"].time().isoformat(),
    }

def list_weekly_availability_serial(availabilities) -> list:
    return [individual_weekly_availability_serial(availability) for availability in availabilities]

def individual_blocked_slot_serial(blocked_slot) -> dict:
    return {
        "id": str(blocked_slot["_id"]),
        "specialist_id": blocked_slot["specialist_id"],
        "start_datetime": blocked_slot["start_datetime"].isoformat(),
        "end_datetime": blocked_slot["end_datetime"].isoformat(),
        "reason": blocked_slot.get("reason"),
        "recurrence_rule": blocked_slot.get("recurrence_rule"),
    }

def list_blocked_slot_serial(blocked_slots) -> list:
    return [individual_blocked_slot_serial(blocked_slot) for blocked_slot in blocked_slots]
