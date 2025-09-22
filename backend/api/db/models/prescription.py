# db/models/prescription.py

def individual_serial(prescription) -> dict:
    return {
        "id": str(prescription["_id"]),
        "medication_name": prescription.get("medication_name"),
        "dosage": prescription.get("dosage"),
        "route": prescription.get("route"),
        "frequency": prescription.get("frequency"),
        "start_date": prescription.get("start_date"),
        "end_date": prescription.get("end_date"),
        "notes": prescription.get("notes"),
        "prescribed_by": prescription.get("prescribed_by"),
        "prescribed_to": prescription.get("prescribed_to"),
        "created_at": prescription.get("created_at"),
        "updated_at": prescription.get("updated_at")
    }

def list_serial(prescriptions) -> list:
    return [individual_serial(p) for p in prescriptions]