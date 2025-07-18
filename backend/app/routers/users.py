from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from passlib.context import CryptContext
from schemas.user import User, UserOut, UserCreate
from db.models.user import individual_serial, list_serial
from db.client import collection_name
from bson import ObjectId
from typing import List
from datetime import datetime, date, timedelta
import os

router = APIRouter()

SECRET_KEY = "g745j7tcgcg4htc834qc8ct934ht3"  # Change in production
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

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
    user = collection_name.find_one({"username": username})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return individual_serial(user)


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
    user_dict["password"] = crypt.hash(user_dict["password"])
    collection_name.insert_one(user_dict)
    user_dict["id"] = str(user_dict["_id"])
    return UserOut(**user_dict)

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = collection_name.find_one({"username": form_data.username})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Verify password
    if not crypt.verify(form_data.password, user["password"]):
        print("Incorrect passworddont match")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate JWT token
    access_token = jwt.encode(
        {"sub": user["_id"], "exp": datetime.utcnow() + timedelta(minutes=30)},
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


    