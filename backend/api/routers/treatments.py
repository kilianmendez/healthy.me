from fastapi import APIRouter, HTTPException, status, Depends
from api.schemas.treatment import Treatment, TreatmentOut, TreatmentUpdate
from api.db.client import treatments_collection
from bson import ObjectId
from typing import List
from datetime import datetime, date
from api.routers.auth import get_current_user
from typing import Optional
from fastapi import Query

router = APIRouter()

# ----------Functions-----------
def convert_dates_to_datetime(data):
    if isinstance(data, dict):
        return {k: convert_dates_to_datetime(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_dates_to_datetime(item) for item in data]
    elif isinstance(data, date) and not isinstance(data, datetime):
        return datetime.combine(data, datetime.min.time())
    else:
        return data

def only_specialists(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "specialist":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action"
        )
    return current_user
# -------------------------------

# ----------Endpoints-----------
@router.post("/", response_model=TreatmentOut, status_code=status.HTTP_201_CREATED)
async def create_treatment(treatment: Treatment, current_user: dict = Depends(only_specialists)):
    treatment_data = treatment.dict()
    treatment_data["prescribed_by"] = current_user["id"]
    treatment_data = convert_dates_to_datetime(treatment_data)

    # Prescriptions are now embedded, so they are saved directly with the treatment
    result = treatments_collection.insert_one(treatment_data)
    if not result.acknowledged:
        raise HTTPException(status_code=500, detail="Failed to create treatment")

    created = treatments_collection.find_one({"_id": result.inserted_id})
    return TreatmentOut(id=str(created["_id"]), **created)

@router.get("/", response_model=List[TreatmentOut])
async def list_treatments(skip: int = 0, limit: int = 10, current_user: dict = Depends(get_current_user)):
    query = {}
    role = current_user.get("role")
    user_id = current_user.get("id")

    if role == "admin":
        pass  # Admins can see all treatments
    elif role == "specialist":
        query["prescribed_by"] = user_id
    elif role == "patient":
        query["prescribed_to"] = user_id
    else:
        raise HTTPException(status_code=403, detail="You do not have permission to view treatments.")

    treatments = treatments_collection.find(query).skip(skip).limit(limit)
    return [TreatmentOut(id=str(t["_id"]), **t) for t in treatments]

@router.get("/{treatment_id}", response_model=TreatmentOut)
async def get_treatment(treatment_id: str, current_user: dict = Depends(get_current_user)):
    treatment = treatments_collection.find_one({"_id": ObjectId(treatment_id)})
    if not treatment:
        raise HTTPException(status_code=404, detail="Treatment not found")

    role = current_user.get("role")
    user_id = current_user.get("id")

    if role == "admin":
        pass
    elif role == "specialist" and treatment.get("prescribed_by") == user_id:
        pass
    elif role == "patient" and treatment.get("prescribed_to") == user_id:
        pass
    else:
        raise HTTPException(status_code=403, detail="You do not have permission to view this treatment.")

    return TreatmentOut(id=str(treatment["_id"]), **treatment)

@router.put("/{treatment_id}", response_model=TreatmentOut)
async def update_treatment(treatment_id: str, treatment_update: TreatmentUpdate, current_user: dict = Depends(get_current_user)):
    treatment = treatments_collection.find_one({"_id": ObjectId(treatment_id)})
    if not treatment:
        raise HTTPException(status_code=404, detail="Treatment not found")

    # Check if the user is the specialist who created the treatment
    if current_user.get("role") != "specialist" or treatment.get("prescribed_by") != current_user.get("id"):
        raise HTTPException(status_code=403, detail="You do not have permission to update this treatment.")

    update_data = treatment_update.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()
    update_data = convert_dates_to_datetime(update_data)

    updated = treatments_collection.find_one_and_update(
        {"_id": ObjectId(treatment_id)},
        {"$set": update_data},
        return_document=True
    )

    if not updated:
        raise HTTPException(status_code=404, detail="Failed to update treatment")
    
    return TreatmentOut(id=str(updated["_id"]), **updated)

@router.delete("/{treatment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_treatment(treatment_id: str, current_user: dict = Depends(get_current_user)):
    treatment = treatments_collection.find_one({"_id": ObjectId(treatment_id)})
    if not treatment:
        raise HTTPException(status_code=404, detail="Treatment not found")

    role = current_user.get("role")
    user_id = current_user.get("id")

    if role != "admin" and treatment.get("prescribed_by") != user_id:
        raise HTTPException(status_code=403, detail="You do not have permission to delete this treatment.")

    result = treatments_collection.delete_one({"_id": ObjectId(treatment_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Treatment not found during deletion")
    
    return {"message": "Treatment deleted successfully"}