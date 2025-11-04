def individual_serial(time_off) -> dict:
    return {
        "id": str(time_off["_id"]),
        "specialist_id": time_off.get("specialist_id"),
        "start_datetime": time_off.get("start_datetime"),
        "end_datetime": time_off.get("end_datetime"),
        "reason": time_off.get("reason")
    }

def list_serial(time_offs) -> list:
    return [individual_serial(time_off) for time_off in time_offs]
