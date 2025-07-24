# db/models/prescription.py

def individual_serial(prescription) -> dict:
    return {
        "id": str(prescription["_id"]),
        "medication_name": prescription.get("medication_name"),
        "dosage": prescription.get("dosage"),
        "route": prescription.get("route"),
        "frequency": prescription.get("frequency"),
        "start_date": prescription.get("start_date").isoformat() if prescription.get("start_date") else None,
        "end_date": prescription.get("end_date").isoformat() if prescription.get("end_date") else None,
        "notes": prescription.get("notes"),
        "prescribed_by": prescription.get("prescribed_by"),
        "prescribed_to": prescription.get("prescribed_to")
    }

def list_serial(prescriptions) -> list:
    return [individual_serial(p) for p in prescriptions]
