from fastapi import APIRouter, HTTPException, status, Depends, File, UploadFile
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from passlib.context import CryptContext
from schemas.user import User, UserOut, UserCreate
from schemas.patient import Patient, PatientRegister, PatientPrivate, PatientPublic
from schemas.specialist import Specialist, SpecialistRegister, SpecialistOut
from db.models.user import individual_serial, list_serial
from db.client import users_collection
from bson import ObjectId
from typing import List, Optional
from datetime import datetime, date, timedelta
import os
import secrets
from utils.security import validate_password_strength
import shutil
import uuid

router = APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY_AUTH")  # Change in production
if not SECRET_KEY or len(SECRET_KEY) < 32:
    raise RuntimeError("SECRET_KEY environment variable not set or is too short (must be at least 32 characters)")
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

crypt = CryptContext(schemes=["bcrypt"])

# ----------Funtions-----------
def is_image(filename: str) -> bool:
    """Check if the file has an image extension."""
    allowed_extensions = {".png", ".jpg", ".jpeg"}
    ext = os.path.splitext(filename)[1].lower()
    return ext in allowed_extensions

def save_avatar(avatar: UploadFile) -> str:
    """Save the avatar with a unique filename and return the path."""
    if not is_image(avatar.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only .png, .jpg, and .jpeg files are allowed."
        )

    file_extension = os.path.splitext(avatar.filename)[1]
    file_name = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join("uploads", "avatars", file_name)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(avatar.file, buffer)
    except Exception as e:
        # Handle potential file system errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not save avatar: {e}"
        )

    return file_path

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

def generate_unique_patient_code():
    """Generates a unique 8-character hexadecimal code."""
    while True:
        code = secrets.token_hex(4).upper()
        if users_collection.find_one({"patient_code": code}) is None:
            return code

def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Decodifica el JWT y retorna el usuario actual.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if user is None:
        raise credentials_exception

    user["id"] = str(user["_id"])
    del user["_id"]
    if "password" in user:
        del user["password"]

    # Convert datetime to date for Pydantic model compatibility
    if "updated_at" in user and isinstance(user["updated_at"], datetime):
        user["updated_at"] = user["updated_at"].date()
    if "created_at" in user and isinstance(user["created_at"], datetime):
        user["created_at"] = user["created_at"].date()
        
    return user
# -------------------------------


# ----------Endpoints-----------
@router.get("/me", response_model=UserOut)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    """
    Retrieve the current user's information.
    """
    return current_user

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users_collection.find_one({"username": form_data.username})
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
        {"sub": str(user["_id"]), "exp": datetime.utcnow() + timedelta(minutes=30)},
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

@router.post("/register", response_model=PatientPrivate, status_code=201)
async def register(patient: PatientRegister = Depends(), avatar: Optional[UploadFile] = File(None)):
    existing = users_collection.find_one({"email": patient.email})
    if existing:
        raise HTTPException(status_code=400, detail="A user with this email already exists")

    validate_password_strength(patient.password)

    patient_dict = patient.dict()
    patient_dict["_id"] = ObjectId()
    patient_dict["password"] = crypt.hash(patient_dict["password"])
    patient_dict["created_at"] = datetime.combine(date.today(), datetime.min.time())
    patient_dict["patient_code"] = generate_unique_patient_code()
    patient_dict["role"] = "patient"

    if avatar:
        patient_dict["avatar_url"] = save_avatar(avatar)
    else:
        patient_dict["avatar_url"] = "uploads/avatars/placeholder/default_patient.jpg"

    patient_dict = convert_dates_to_datetime(patient_dict)

    users_collection.insert_one(patient_dict)
    patient_dict["id"] = str(patient_dict["_id"])
    return PatientPrivate(**patient_dict)


@router.post("/register/specialist", response_model=SpecialistOut, status_code=201)
async def register_specialist(specialist: SpecialistRegister = Depends(), avatar: Optional[UploadFile] = File(None)):
    existing = users_collection.find_one({"email": specialist.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    validate_password_strength(specialist.password)

    specialist_dict = specialist.dict()
    specialist_dict["_id"] = ObjectId()
    specialist_dict["password"] = crypt.hash(specialist_dict["password"])
    specialist_dict["created_at"] = datetime.combine(date.today(), datetime.min.time())
    specialist_dict["role"] = "specialist"
    specialist_dict["is_verified"] = False

    if avatar:
        specialist_dict["avatar_url"] = save_avatar(avatar)
    else:
        specialist_dict["avatar_url"] = "uploads/avatars/placeholder/default_specialist.jpg"

    specialist_dict = convert_dates_to_datetime(specialist_dict)

    users_collection.insert_one(specialist_dict)
    specialist_dict["id"] = str(specialist_dict["_id"])
    return SpecialistOut(**specialist_dict)

@router.put("/toggle-admin/{user_id}", response_model=UserOut)
async def toggle_admin_role(user_id: str, current_user: dict = Depends(get_current_user)):
    """
    Toggle the admin role of a user.
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para modificar roles"
        )

    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    current_role = user.get("role", "patient")
    
    if current_role not in ["admin", "patient"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se puede modificar el rol de un {current_role}"
        )

    new_role = "patient" if current_role == "admin" else "admin"

    updated = users_collection.find_one_and_update(
        {"_id": ObjectId(user_id)},
        {"$set": {"role": new_role, "updated_at": datetime.utcnow()}},
        return_document=True
    )
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Error al actualizar el usuario")

    updated["id"] = str(updated["_id"])
    updated.pop("_id", None)
    updated.pop("password", None)

    # ✅ Solución: convertir a date exacto
    if "updated_at" in updated and isinstance(updated["updated_at"], datetime):
        updated["updated_at"] = updated["updated_at"].date()
    if "created_at" in updated and isinstance(updated["created_at"], datetime):
        updated["created_at"] = updated["created_at"].date()

    return UserOut(**updated)






