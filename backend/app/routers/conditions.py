from fastapi import APIRouter, HTTPException, status
from schemas.condition import Condition, ConditionOut, ConditionStatus, ConditionUpdate
from db.client import conditions_collection
from bson import ObjectId
from typing import List
from datetime import datetime, date
from typing import Optional


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

def convert_datetime_to_date_fields(data: dict, date_fields: List[str]):
    for field in date_fields:
        if field in data and isinstance(data[field], datetime):
            data[field] = data[field].date()
    return data

# -------------------------------

# ----------Endpoints-----------

@router.post("/", response_model=ConditionOut, status_code=status.HTTP_201_CREATED)
async def create_condition(condition: Condition):
    condition_data = condition.dict()
    condition_data = convert_dates_to_datetime(condition_data)

    result = conditions_collection.insert_one(condition_data)
    if not result.acknowledged:
        raise HTTPException(status_code=500, detail="Failed to create condition")

    created = conditions_collection.find_one({"_id": result.inserted_id})
    convert_datetime_to_date_fields(created, ["diagnosed_at"])

    return ConditionOut(id=str(created["_id"]), **created)

@router.get("/search", response_model=List[ConditionOut])
async def search_conditions(
    diagnosed_to: Optional[str] = None,
    diagnosed_by: Optional[str] = None,
    status: Optional[ConditionStatus] = None,
    name: Optional[str] = None,
    diagnosed_at_from: Optional[date] = None,
    diagnosed_at_to: Optional[date] = None,
    skip: int = 0,
    limit: int = 10
):
    """Search conditions with optional filters."""
    query = {}

    if diagnosed_to:
        query["diagnosed_to"] = diagnosed_to

    if diagnosed_by:
        query["diagnosed_by"] = diagnosed_by

    if status:
        query["status"] = status

    if name:
        regex = ".*" + ".*".join(name) + ".*"
        query["name"] = {"$regex": regex, "$options": "i"}

    if diagnosed_at_from or diagnosed_at_to:
        query["diagnosed_at"] = {}
        if diagnosed_at_from:
            query["diagnosed_at"]["$gte"] = datetime.combine(diagnosed_at_from, datetime.min.time())
        if diagnosed_at_to:
            query["diagnosed_at"]["$lte"] = datetime.combine(diagnosed_at_to, datetime.min.time())

    conditions = conditions_collection.find(query).skip(skip).limit(limit)
    result = []
    for c in conditions:
        convert_datetime_to_date_fields(c, ["diagnosed_at"])
        result.append(ConditionOut(id=str(c["_id"]), **c))

    return result

@router.get("/by-patient/{patient_id}", response_model=List[ConditionOut])
async def get_conditions_by_patient(patient_id: str, skip: int = 0, limit: int = 10):
    """Get all medical conditions for a specific patient."""
    conditions = conditions_collection.find({"diagnosed_to": patient_id}).skip(skip).limit(limit)
    
    result = []
    for c in conditions:
        convert_datetime_to_date_fields(c, ["diagnosed_at"])
        result.append(ConditionOut(id=str(c["_id"]), **c))
    
    return result

@router.get("/by-specialist/{specialist_id}", response_model=List[ConditionOut])
async def get_conditions_by_specialist(specialist_id: str, skip: int = 0, limit: int = 10):
    """Get all medical conditions diagnosed by a specific specialist."""
    conditions = conditions_collection.find({"diagnosed_by": specialist_id}).skip(skip).limit(limit)
    
    result = []
    for c in conditions:
        convert_datetime_to_date_fields(c, ["diagnosed_at"])
        result.append(ConditionOut(id=str(c["_id"]), **c))
    
    return result

@router.get("/", response_model=List[ConditionOut])
async def get_conditions(skip: int = 0, limit: int = 10):
    conditions = conditions_collection.find().skip(skip).limit(limit)
    result = []
    for c in conditions:
        convert_datetime_to_date_fields(c, ["diagnosed_at"])
        result.append(ConditionOut(id=str(c["_id"]), **c))
    return result

@router.get("/{condition_id}", response_model=ConditionOut)
async def get_condition(condition_id: str):
    condition = conditions_collection.find_one({"_id": ObjectId(condition_id)})
    if not condition:
        raise HTTPException(status_code=404, detail="Condition not found")

    convert_datetime_to_date_fields(condition, ["diagnosed_at"])
    return ConditionOut(id=str(condition["_id"]), **condition)

@router.put("/{condition_id}", response_model=ConditionOut)
async def update_condition(condition_id: str, condition_update: ConditionUpdate):
    update_data = condition_update.dict(exclude_unset=True)
    update_data = convert_dates_to_datetime(update_data)

    updated = conditions_collection.find_one_and_update(
        {"_id": ObjectId(condition_id)},
        {"$set": update_data},
        return_document=True
    )

    if not updated:
        raise HTTPException(status_code=404, detail="Condition not found or no changes made")

    convert_datetime_to_date_fields(updated, ["diagnosed_at"])
    return ConditionOut(id=str(updated["_id"]), **updated)

@router.delete("/{condition_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_condition(condition_id: str):
    result = conditions_collection.delete_one({"_id": ObjectId(condition_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Condition not found")
    return {"message": "Condition deleted successfully"}





# -------------------------------
