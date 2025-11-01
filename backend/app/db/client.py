from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

# MongoDB connection
client = MongoClient(os.getenv("MONGODB_URI"))
db_client = client.medical_tracker
users_collection = db_client["users"]
diagnoses_collection = db_client["diagnoses"]
treatments_collection = db_client["treatments"]
appointments_collection = db_client["appointments"]
consultations_collection = db_client["consultations"]
prescriptions_collection = db_client["prescriptions"]
weekly_availabilities_collection = db_client["weekly_availabilities"]
blocked_slots_collection = db_client["blocked_slots"]