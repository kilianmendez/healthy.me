def individual_serial(appointment) -> dict:
    return {
        "id": str(appointment["_id"]),
        "date": appointment.get("date").isoformat() if appointment.get("date") else None,
        "specialist_id": appointment.get("specialist_id"),
        "patient_id": appointment.get("patient_id"),
        "reason": appointment.get("reason"),
        "notes": appointment.get("notes"),
        "location": appointment.get("location"),
        "status": appointment.get("status", "scheduled")
    }

def list_serial(appointments) -> list:
    """
    Serializes a list of appointment objects into a list of dictionaries.
    Args:
        appointments (list): A list of appointment objects to serialize.
    Returns:
        list: A list of dictionaries representing the appointment objects.
    """
    return [individual_serial(appointment) for appointment in appointments]