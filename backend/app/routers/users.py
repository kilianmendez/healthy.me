from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from passlib.context import CryptContext
from schemas.user import User, UserOut, UserCreate, UserRole, Gender
from db.models.user import individual_serial, list_serial
from db.client import users_collection
from bson import ObjectId
from typing import List
from datetime import datetime, date, timedelta
import os
from .auth import get_current_user
import re
from utils.security import validate_password_strength
from fastapi import Query
from typing import Optional

router = APIRouter()

crypt = CryptContext(schemes=["bcrypt"])

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

@router.get("/search", response_model=List[UserOut])
async def search_users(
    username: Optional[str] = Query(None, description="Username to search (partial, case-insensitive)"),
    email: Optional[str] = Query(None, description="Email to search (partial, case-insensitive)"),
    full_name: Optional[str] = Query(None, description="Full name to search (partial, case-insensitive)"),
    gender: Optional[Gender] = Query(None, description="Gender filter"),
    date_of_birth: Optional[date] = Query(None, description="Exact date of birth"),
    role: Optional[UserRole] = Query(None, description="User role"),
    disabled: Optional[bool] = Query(None, description="Filter by disabled status"),
    created_at: Optional[date] = Query(None, description="Exact creation date"),
    updated_at: Optional[date] = Query(None, description="Exact last update date"),
    avatar_url: Optional[str] = Query(None, description="Avatar URL to search (partial, case-insensitive)"),
    current_user: dict = Depends(get_current_user)
):
    
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can access this resource"
        )

    query = {}

    if username:
        query["username"] = {"$regex": re.escape(username), "$options": "i"}
    if email:
        query["email"] = {"$regex": re.escape(email), "$options": "i"}
    if full_name:
        query["full_name"] = {"$regex": re.escape(full_name), "$options": "i"}
    if gender:
        query["gender"] = gender.value
    if date_of_birth:
        # Convert date to datetime for matching in DB
        dt_start = datetime.combine(date_of_birth, datetime.min.time())
        dt_end = datetime.combine(date_of_birth, datetime.max.time())
        query["date_of_birth"] = {"$gte": dt_start, "$lte": dt_end}
    if role:
        query["role"] = role.value
    if disabled is not None:
        query["disabled"] = disabled
    if created_at:
        dt_start = datetime.combine(created_at, datetime.min.time())
        dt_end = datetime.combine(created_at, datetime.max.time())
        query["created_at"] = {"$gte": dt_start, "$lte": dt_end}
    if updated_at:
        dt_start = datetime.combine(updated_at, datetime.min.time())
        dt_end = datetime.combine(updated_at, datetime.max.time())
        query["updated_at"] = {"$gte": dt_start, "$lte": dt_end}
    if avatar_url:
        query["avatar_url"] = {"$regex": re.escape(avatar_url), "$options": "i"}

    users_cursor = users_collection.find(query)

    result = []
    for user in users_cursor:
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


