from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
import jwt
from schemas.user import User, UserOut, UserCreate, Specialist, SpecialistCreate, Patient
from db.models.user import individual_serial, list_serial
from db.client import collection_name
from bson import ObjectId
from typing import List
from datetime import datetime, date
import os

router = APIRouter()

SECRET_KEY = os.getenv("JWT_SECRET", "your-secret-key")  # Change in production
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

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
# -------------------------------


# ----------Base User-----------
@router.get("/", response_model=List[UserOut])
async def get_users():
    """
    Retrieve a list of all users.
    """
    users = collection_name.find()
    return list_serial(users)

@router.get("/{user_id}", response_model=UserOut)
async def get_user(user_id: str):
    """
    Retrieve a specific user by ID.
    """
    user = collection_name.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return individual_serial(user)

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    """
    Create a new user.
    """
    user_dict = user.dict()
    user_dict["created_at"] = datetime.combine(date.today(), datetime.min.time())
    user_dict = convert_dates_to_datetime(user_dict)
    user_dict["_id"] = ObjectId()
    collection_name.insert_one(user_dict)
    user_dict["id"] = str(user_dict["_id"])
    return UserOut(**user_dict)

# ---------------Specialist----------------

@router.post("/specialist/", response_model=Specialist, status_code=status.HTTP_201_CREATED)
async def create_specialist(specialist: SpecialistCreate):
    """
    Create a new specialist.
    """
    specialist_dict = specialist.dict()
    specialist_dict["created_at"] = datetime.combine(date.today(), datetime.min.time())
    specialist_dict = convert_dates_to_datetime(specialist_dict)
    specialist_dict["_id"] = ObjectId()
    collection_name.insert_one(specialist_dict)
    specialist_dict["id"] = str(specialist_dict["_id"])
    return Specialist(**specialist_dict)

@router.get("/specialist/{specialist_id}", response_model=Specialist)
async def get_specialist(specialist_id: str):
    """
    Retrieve a specific specialist by ID.
    """
    specialist = collection_name.find_one({"_id": ObjectId(specialist_id), "role": "specialist"})
    if not specialist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Specialist not found")
    return individual_serial(specialist)

@router.get("/specialists/", response_model=List[Specialist])
async def get_specialists():
    """
    Retrieve a list of all specialists.
    """
    specialists = collection_name.find({"role": "specialist"})
    return list_serial(specialists)