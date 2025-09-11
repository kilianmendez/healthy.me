from fastapi import APIRouter, HTTPException, status
from schemas.condition import Condition, ConditionOut, ConditionUpdate
from db.client import conditions_collection
from bson import ObjectId
from typing import List
from typing import Optional

router = APIRouter()

# ----------Endpoints-----------

@router.post("/", response_model=ConditionOut, status_code=status.HTTP_201_CREATED)
async def create_condition(condition: Condition):
    condition_data = condition.dict()

    result = conditions_collection.insert_one(condition_data)
    if not result.acknowledged:
        raise HTTPException(status_code=500, detail="Failed to create condition")

    created = conditions_collection.find_one({"_id": result.inserted_id})

    return ConditionOut(id=str(created["_id"]), **created)

@router.get("/search", response_model=List[ConditionOut])
async def search_conditions(
    name: Optional[str] = None,
    skip: int = 0,
    limit: int = 10
):
    """Search conditions with optional filters."""
    query = {}

    if name:
        regex = ".*" + ".*".join(name) + ".*"
        query["name"] = {"$regex": regex, "$options": "i"}

    conditions = conditions_collection.find(query).skip(skip).limit(limit)
    result = []
    for c in conditions:
        result.append(ConditionOut(id=str(c["_id"]), **c))

    return result

@router.get("/", response_model=List[ConditionOut])
async def get_conditions(skip: int = 0, limit: int = 10):
    conditions = conditions_collection.find().skip(skip).limit(limit)
    result = []
    for c in conditions:
        result.append(ConditionOut(id=str(c["_id"]), **c))
    return result

@router.get("/{condition_id}", response_model=ConditionOut)
async def get_condition(condition_id: str):
    condition = conditions_collection.find_one({"_id": ObjectId(condition_id)})
    if not condition:
        raise HTTPException(status_code=404, detail="Condition not found")

    return ConditionOut(id=str(condition["_id"]), **condition)

@router.put("/{condition_id}", response_model=ConditionOut)
async def update_condition(condition_id: str, condition_update: ConditionUpdate):
    update_data = condition_update.dict(exclude_unset=True)

    updated = conditions_collection.find_one_and_update(
        {"_id": ObjectId(condition_id)},
        {"$set": update_data},
        return_document=True
    )

    if not updated:
        raise HTTPException(status_code=404, detail="Condition not found or no changes made")

    return ConditionOut(id=str(updated["_id"]), **updated)

@router.delete("/{condition_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_condition(condition_id: str):
    result = conditions_collection.delete_one({"_id": ObjectId(condition_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Condition not found")
    return {"message": "Condition deleted successfully"}