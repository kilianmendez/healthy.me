from app.db.client import db_client, users_collection, diagnoses_collection, prescriptions_collection, treatments_collection, appointments_collection, consultations_collection

def clear_all_collections():
    print("Clearing all collections...")
    users_collection.drop()
    diagnoses_collection.drop()
    prescriptions_collection.drop()
    treatments_collection.drop()
    appointments_collection.drop()
    consultations_collection.drop()
    print("All collections cleared.")

if __name__ == "__main__":
    clear_all_collections()
