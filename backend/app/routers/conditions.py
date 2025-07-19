from fastapi import APIRouter, HTTPException, status, Depends
from passlib.context import CryptContext
from schemas.condition import Condition, ConditionOut
from db.models.user import individual_serial, list_serial
from db.client import conditions_collection
from bson import ObjectId
from typing import List
from datetime import datetime, date, timedelta
import os

router = APIRouter()

# ----------Functions-----------

# -------------------------------


# ----------Endpoints-----------
@router.post("/", response_model=ConditionOut, status_code=status.HTTP_201_CREATED)
async def create_condition(condition: Condition):
    condition_data = condition.dict()
    if not condition_data.get("diagnosed_at"):
        # Ponemos la fecha actual con hora 00:00:00 para que sea datetime.datetime
        condition_data["diagnosed_at"] = datetime.now()
    else:
        # Si viene un datetime.date, lo convertimos a datetime.datetime a medianoche
        if isinstance(condition_data["diagnosed_at"], date) and not isinstance(condition_data["diagnosed_at"], datetime):
            diagnosed_date = condition_data["diagnosed_at"]
            condition_data["diagnosed_at"] = datetime(diagnosed_date.year, diagnosed_date.month, diagnosed_date.day)
    
    result = conditions_collection.insert_one(condition_data)
    if not result.acknowledged:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create condition")
    
    created_condition = conditions_collection.find_one({"_id": result.inserted_id})
    return ConditionOut(id=str(created_condition["_id"]), **created_condition)

@router.get("/", response_model=List[ConditionOut])
async def get_conditions():
    """
    Retrieve all conditions.
    """
    conditions = conditions_collection.find()
    return [ConditionOut(id=str(condition["_id"]), **condition) for condition in conditions]

@router.get("/{condition_id}", response_model=ConditionOut)
async def get_condition(condition_id: str):
    """
    Retrieve a specific condition by ID.
    """
    condition = conditions_collection.find_one({"_id": ObjectId(condition_id)})
    if not condition:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Condition not found")
    return ConditionOut(id=str(condition["_id"]), **condition)

@router.put("/{condition_id}", response_model=ConditionOut)
async def update_condition(condition_id: str, condition_update: Condition):
    """
    Update an existing condition.
    """
    condition_data = condition_update.dict()
    if not condition_data.get("diagnosed_at"):
        # Ponemos la fecha actual con hora 00:00:00 para que sea datetime.datetime
        condition_data["diagnosed_at"] = datetime.now()
    else:
        # Si viene un datetime.date, lo convertimos a datetime.datetime a medianoche
        if isinstance(condition_data["diagnosed_at"], date) and not isinstance(condition_data["diagnosed_at"], datetime):
            diagnosed_date = condition_data["diagnosed_at"]
            condition_data["diagnosed_at"] = datetime(diagnosed_date.year, diagnosed_date.month, diagnosed_date.day)
    
    result = conditions_collection.update_one({"_id": ObjectId(condition_id)}, {"$set": condition_data})
    if result.modified_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Condition not found or no changes made")
    
    updated_condition = conditions_collection.find_one({"_id": ObjectId(condition_id)})
    return ConditionOut(id=str(updated_condition["_id"]), **updated_condition)

@router.delete("/{condition_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_condition(condition_id: str):
    """
    Delete a condition by ID.
    """
    result = conditions_collection.delete_one({"_id": ObjectId(condition_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Condition not found")
    return {"message": "Condition deleted successfully"}
# -------------------------------


