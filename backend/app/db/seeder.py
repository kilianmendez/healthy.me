import datetime
from datetime import date, timedelta
from typing import List
from bson import ObjectId
import random

from db.client import users_collection
from schemas.specialist import UserRole, Gender
from utils.security import get_password_hash

def seed_database():
    if users_collection.count_documents({}) > 0:
        print("Database is not empty. Skipping seeding.")
        return

    print("Seeding database with initial data...")

    # Admin User
    admin_username = "Admin"
    admin_password_raw = f"{admin_username}@1234"
    admin_password_hashed = get_password_hash(admin_password_raw)
    admin_user = {
        "_id": ObjectId(),
        "username": admin_username.lower(),
        "email": "admin@gmail.com",
        "password": admin_password_hashed,
        "full_name": "Admin User",
        "role": "admin",
        "disabled": False,
        "created_at": datetime.datetime.utcnow(),
        "updated_at": datetime.datetime.utcnow(),
        "date_of_birth": datetime.datetime.combine(date(1980, 5, 15), datetime.datetime.min.time()),
        "gender": Gender.other.value,
        "avatar_url": None
    }
    users_collection.insert_one(admin_user)
    print("Admin user created.")

    print("Database seeding complete.")
