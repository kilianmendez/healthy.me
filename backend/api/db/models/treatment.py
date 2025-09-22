def individual_serial(treatment) -> dict:
    return {
        "id": str(treatment["_id"]),
        "name": treatment.get("name"),
        "description": treatment.get("description"),
        "observations": treatment.get("observations"),
        "type": treatment.get("type"),
        "prescribed_by": treatment.get("prescribed_by"),
        "prescribed_to": treatment.get("prescribed_to"),
        "prescriptions": [str(prescription) for prescription in treatment.get("prescriptions", [])],
        "prescription_ids": treatment.get("prescription_ids", []),  # <-- este es el campo que guarda los IDs reales
        "status": treatment.get("status", "ongoing"),
        "start_date": treatment.get("start_date").isoformat() if treatment.get("start_date") else None,
        "end_date": treatment.get("end_date").isoformat() if treatment.get("end_date") else None,
        "outcome": treatment.get("outcome")
    }

def list_serial(treatments) -> list:
    """
    Serializes a list of treatment objects into a list of dictionaries.
    Args:
        treatments (list): A list of treatment objects to serialize.
    Returns:
        list: A list of dictionaries representing the treatment objects.
    """
    return [individual_serial(treatment) for treatment in treatments]