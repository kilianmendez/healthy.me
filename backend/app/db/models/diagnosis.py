# db/models/diagnosis.py

def individual_serial(diagnosis) -> dict:
    return {
        "id": str(diagnosis["_id"]),
        "condition_id": diagnosis.get("condition_id"),
        "patient_id": diagnosis.get("patient_id"),
        "specialist_id": diagnosis.get("specialist_id"),
        "diagnosed_at": diagnosis.get("diagnosed_at").isoformat() if diagnosis.get("diagnosed_at") else None,
        "symptoms": diagnosis.get("symptoms", []),
        "observations": diagnosis.get("observations"),
        "status": diagnosis.get("status", "active")
    }

def list_serial(diagnoses) -> list:
    """
    Serializes a list of diagnosis objects into a list of dictionaries.
    Args:
        diagnoses (list): A list of diagnosis objects to serialize.
    Returns:
        list: A list of dictionaries representing the diagnosis objects.
    """
    return [individual_serial(diagnosis) for diagnosis in diagnoses]
