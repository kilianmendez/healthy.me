def individual_serial(consultation) -> dict:
    return {
        "id": str(consultation["_id"]),
        "date": consultation.get("date").isoformat() if consultation.get("date") else None,
        "specialist_id": consultation.get("specialist_id"),
        "patient_id": consultation.get("patient_id"),
        "reason": consultation.get("reason"),
        "notes": consultation.get("notes"),
        "diagnosis": consultation.get("diagnosis"),
        "follow_up_required": consultation.get("follow_up_required", False),
        "prescriptions": [str(prescription) for prescription in consultation.get("prescriptions", [])],
        "treatments": [str(treatment) for treatment in consultation.get("treatments", [])],
        "appointment_id": consultation.get("appointment_id"),
    }

def list_serial(consultations) -> list:
    """
    Serializes a list of consultation objects into a list of dictionaries.
    Args:
        consultations (list): A list of consultation objects to serialize.
    Returns:
        list: A list of dictionaries representing the consultation objects.
    """
    return [individual_serial(consultation) for consultation in consultations]