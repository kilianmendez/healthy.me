def individual_serial(user) -> dict:
    return {
        "id": str(user["_id"]),
        "username": user.get("username"),
        "email": user.get("email"),
        "full_name": user.get("full_name"),
        "gender": user.get("gender"),
        "date_of_birth": user.get("date_of_birth").isoformat() if user.get("date_of_birth") else None,
        "role": user.get("role", "patient"),
        "disabled": user.get("disabled", False),
        "created_at": user.get("created_at").isoformat() if user.get("created_at") else None,
        "updated_at": user.get("updated_at").isoformat() if user.get("updated_at") else None,
        "avatar_url": user.get("avatar_url"),
        "phone_number": user.get("phone_number"),
        "emergency_contact": user.get("emergency_contact"),
        "conditions": user.get("conditions", []),
        "treatments": user.get("treatments", []),
        "medications": user.get("medications", []),
        "allergies": user.get("allergies", []),
        "appointments": user.get("appointments", []),
        "consultation_history": user.get("consultation_history", []),
        "prescriptions": user.get("prescriptions", []),
        "workplaces": user.get("workplaces", []),
        "available_hours": user.get("available_hours"),
        "specialties": user.get("specialties", []),
        "biography": user.get("biography"),
        "certifications": user.get("certifications", []),
        "patients": user.get("patients", [])
    }

def list_serial(users) -> list:
    """
    Serializes a list of user objects into a list of dictionaries.
    Args:
        users (list): A list of user objects to serialize.
    Returns:
        list: A list of dictionaries representing the user objects.
    """
    return [individual_serial(user) for user in users]