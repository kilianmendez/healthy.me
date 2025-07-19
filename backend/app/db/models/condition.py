def individual_serial(condition) -> dict:
    return {
        "id": str(condition["_id"]),
        "name": condition.get("name"),
        "description": condition.get("description"),
        "symptoms": condition.get("symptoms", []),
        "observations": condition.get("observations"),
        "diagnosed_by": condition.get("diagnosed_by"),
        "diagnosed_for": condition.get("diagnosed_to"),
        "diagnosed_at": condition.get("diagnosed_at").isoformat() if condition.get("diagnosed_at") else None,
        "status": condition.get("status", "active")
    }

def list_serial(conditions) -> list:
    """
    Serializes a list of condition objects into a list of dictionaries.
    Args:
        conditions (list): A list of condition objects to serialize.
    Returns:
        list: A list of dictionaries representing the condition objects.
    """
    return [individual_serial(condition) for condition in conditions]