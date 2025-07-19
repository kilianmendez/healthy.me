from pymongo import MongoClient
from dotenv import load_dotenv

# MongoDB connection
client = MongoClient("mongodb+srv://kylianmendez:X2gKaohY6PCgUIRK@cluster0.fpavtmz.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db_client = client.medical_tracker
users_collection = db_client["users"]
conditions_collection = db_client["conditions"]
treatments_collection = db_client["treatments"]
appointments_collection = db_client["appointments"]