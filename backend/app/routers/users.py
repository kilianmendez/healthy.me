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
from .auth import get_current_user
import re
from utils.security import validate_password_strength

router = APIRouter()

crypt = CryptContext(schemes=["bcrypt"])

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
async def get_users(current_user: dict = Depends(get_current_user)):
    users = users_collection.find()
    result = []

    for user in users:
        user["id"] = str(user["_id"])
        
        if "updated_at" in user and isinstance(user["updated_at"], datetime):
            user["updated_at"] = user["updated_at"].date()
        if "created_at" in user and isinstance(user["created_at"], datetime):
            user["created_at"] = user["created_at"].date()

        result.append(UserOut(**user))

    return result


@router.get("/{user_id}", response_model=UserOut)
async def get_user(user_id: str, current_user: dict = Depends(get_current_user)):
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user["id"] = str(user["_id"])

    # 👇 Conversión explícita como en specialist
    if "updated_at" in user and isinstance(user["updated_at"], datetime):
        user["updated_at"] = user["updated_at"].date()
    if "created_at" in user and isinstance(user["created_at"], datetime):
        user["created_at"] = user["created_at"].date()

    return UserOut(**user)

@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, current_user: dict = Depends(get_current_user)):
    """
    Create a new user.
    """

    # Verifica si ya existe un usuario con el mismo email
    existing_user = users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists"
        )
    
    validate_password_strength(user.password)

    user_dict = user.dict()
    user_dict["_id"] = ObjectId()
    user_dict["created_at"] = datetime.combine(date.today(), datetime.min.time())
    user_dict["password"] = crypt.hash(user_dict["password"])
    
    user_dict = convert_dates_to_datetime(user_dict)
    users_collection.insert_one(user_dict)

    user_dict["id"] = str(user_dict["_id"])
    return UserOut(**user_dict)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a user by ID.
    Only the user themselves or an admin can perform this action.
    """
    if current_user["role"] != "admin" and current_user["id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this user"
        )

    result = users_collection.delete_one({"_id": ObjectId(user_id)})

    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return {"message": "User deleted successfully"}


# -------------------------------


