from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from passlib.context import CryptContext
from schemas.user import User, UserOut, UserCreate
from db.models.user import individual_serial, list_serial
from db.client import users_collection
from bson import ObjectId
from typing import List
from datetime import datetime, date, timedelta
import os

router = APIRouter()

# ----------Functions-----------
def convert_dates_to_datetime(data):
    from datetime import datetime, date
    if isinstance(data, dict):
        return {k: convert_dates_to_datetime(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_dates_to_datetime(item) for item in data]
    elif isinstance(data, date) and not isinstance(data, datetime):
        return datetime.combine(data, datetime.min.time())
    else:
        return data

def search_user_db(username: str):
    user = users_collection.find_one({"username": username})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return individual_serial(user)
# -------------------------------


# ----------Endpoints-----------
@router.get("/", response_model=List[UserOut])
async def get_users():
    """
    Retrieve a list of all users.
    """
    users = users_collection.find()
    return list_serial(users)

@router.get("/{user_id}", response_model=UserOut)
async def get_user(user_id: str):
    """
    Retrieve a specific user by ID.
    """
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return individual_serial(user)
# -------------------------------


