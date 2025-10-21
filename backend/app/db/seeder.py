from .client import users_collection, diagnoses_collection, prescriptions_collection, treatments_collection, appointments_collection, consultations_collection
from utils.security import get_password_hash
from datetime import datetime, date, timedelta
from bson import ObjectId
import random

def seed_users():
    """
    Seeds the database with initial user data if the users collection is empty.
    Returns a dictionary of inserted users categorized by role.
    """
    if users_collection.count_documents({}) == 0:
        print("Seeding users...")
        users_data = [
            # Admin User
            {
                "username": "admin",
                "email": "admin@example.com",
                "full_name": "Admin User",
                "gender": "other",
                "date_of_birth": datetime(1990, 1, 1),
                "role": "admin",
                "disabled": False,
                "password": get_password_hash("Admin@1234"),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "is_verified": True,
            },
            # Specialists
            {
                "username": "dr.smith",
                "email": "dr.smith@example.com",
                "full_name": "Dr. John Smith",
                "gender": "male",
                "date_of_birth": datetime(1975, 5, 10),
                "role": "specialist",
                "disabled": False,
                "password": get_password_hash("Specialist@1234"),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "is_verified": True,
                "specialties": ["Cardiology"],
                "biography": "Dr. John Smith is a board-certified cardiologist with over 15 years of experience in treating heart conditions. He is a fellow of the American College of Cardiology.",
                "workplaces": ["CardioCare Clinic", "City General Hospital"],
                "available_hours": "Mon-Fri, 9:00 AM - 5:00 PM",
                "certifications": ["Board Certified in Cardiology", "Advanced Cardiac Life Support (ACLS)"],
                "patients": []
            },
            {
                "username": "dr.jones",
                "email": "dr.jones@example.com",
                "full_name": "Dr. Sarah Jones",
                "gender": "female",
                "date_of_birth": datetime(1980, 8, 22),
                "role": "specialist",
                "disabled": False,
                "password": get_password_hash("Specialist@1234"),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "is_verified": True,
                "specialties": ["Dermatology"],
                "biography": "Dr. Sarah Jones is a dermatologist specializing in cosmetic and medical dermatology. She is known for her patient-centered approach and expertise in skin cancer screening.",
                "workplaces": ["Healthy Skin Clinic"],
                "available_hours": "Tue-Sat, 10:00 AM - 6:00 PM",
                "certifications": ["Board Certified in Dermatology"],
                "patients": []
            },
            {
                "username": "dr.williams",
                "email": "dr.williams@example.com",
                "full_name": "Dr. David Williams",
                "gender": "male",
                "date_of_birth": datetime(1968, 11, 30),
                "role": "specialist",
                "disabled": False,
                "password": get_password_hash("Specialist@1234"),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "is_verified": True,
                "specialties": ["Neurology"],
                "biography": "Dr. David Williams has two decades of experience in neurology, with a focus on epilepsy and movement disorders. He is committed to providing comprehensive neurological care.",
                "workplaces": ["NeuroWell Institute"],
                "available_hours": "Mon, Wed, Fri, 8:00 AM - 4:00 PM",
                "certifications": ["Board Certified in Neurology", "Certified in Clinical Neurophysiology"],
                "patients": []
            },
            {
                "username": "dr.brown",
                "email": "dr.brown@example.com",
                "full_name": "Dr. Emily Brown",
                "gender": "female",
                "date_of_birth": datetime(1985, 2, 14),
                "role": "specialist",
                "disabled": False,
                "password": get_password_hash("Specialist@1234"),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "is_verified": True,
                "specialties": ["Pediatrics"],
                "biography": "Dr. Emily Brown is a compassionate pediatrician dedicated to the health and well-being of children. She has a special interest in developmental pediatrics.",
                "workplaces": ["KidsHealth Pediatrics"],
                "available_hours": "Mon-Fri, 8:30 AM - 4:30 PM",
                "certifications": ["Board Certified in Pediatrics"],
                "patients": []
            },
            {
                "username": "dr.davis",
                "email": "dr.davis@example.com",
                "full_name": "Dr. Michael Davis",
                "gender": "male",
                "date_of_birth": datetime(1972, 7, 7),
                "role": "specialist",
                "disabled": False,
                "password": get_password_hash("Specialist@1234"),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "is_verified": True,
                "specialties": ["Orthopedics"],
                "biography": "Dr. Michael Davis is an orthopedic surgeon with expertise in sports medicine and joint replacement. He helps patients regain mobility and return to their active lifestyles.",
                "workplaces": ["OrthoPro Clinic", "University Medical Center"],
                "available_hours": "Tue, Thu, 9:00 AM - 5:00 PM",
                "certifications": ["Board Certified in Orthopedic Surgery", "Fellowship in Sports Medicine"],
                "patients": []
            },
            # Patients
            {
                "username": "johndoe",
                "email": "johndoe@example.com",
                "full_name": "John Doe",
                "gender": "male",
                "date_of_birth": datetime(1992, 3, 15),
                "role": "patient",
                "disabled": False,
                "password": get_password_hash("Patient@1234"),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "is_verified": True,
                "phone_number": "555-123-4567",
                "emergency_contact": "Jane Doe (555-987-6543)",
                "allergies": ["Pollen", "Dust Mites"],
                "medications": ["Loratadine"],
                "treatments": [],
                "consultation_history": [],
                "prescriptions": []
            },
            {
                "username": "janesmith",
                "email": "janesmith@example.com",
                "full_name": "Jane Smith",
                "gender": "female",
                "date_of_birth": datetime(1988, 6, 25),
                "role": "patient",
                "disabled": False,
                "password": get_password_hash("Patient@1234"),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "is_verified": True,
                "phone_number": "555-234-5678",
                "emergency_contact": "John Smith (555-876-5432)",
                "allergies": ["Penicillin"],
                "medications": ["Amoxicillin (allergy)", "Ibuprofen"],
                "treatments": [],
                "consultation_history": [],
                "prescriptions": []
            },
            {
                "username": "peterjones",
                "email": "peterjones@example.com",
                "full_name": "Peter Jones",
                "gender": "male",
                "date_of_birth": datetime(2000, 1, 1),
                "role": "patient",
                "disabled": False,
                "password": get_password_hash("Patient@1234"),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "is_verified": True,
                "phone_number": "555-345-6789",
                "emergency_contact": "Mary Jones (555-765-4321)",
                "allergies": [],
                "medications": [],
                "treatments": [],
                "consultation_history": [],
                "prescriptions": []
            },
            {
                "username": "marywhite",
                "email": "marywhite@example.com",
                "full_name": "Mary White",
                "gender": "female",
                "date_of_birth": datetime(1995, 9, 5),
                "role": "patient",
                "disabled": False,
                "password": get_password_hash("Patient@1234"),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "is_verified": True,
                "phone_number": "555-456-7890",
                "emergency_contact": "David White (555-654-3210)",
                "allergies": ["Latex"],
                "medications": ["Metformin"],
                "treatments": ["Physical Therapy"],
                "consultation_history": [],
                "prescriptions": []
            },
            {
                "username": "kevinbrown",
                "email": "kevinbrown@example.com",
                "full_name": "Kevin Brown",
                "gender": "male",
                "date_of_birth": datetime(1983, 12, 12),
                "role": "patient",
                "disabled": False,
                "password": get_password_hash("Patient@1234"),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "is_verified": True,
                "phone_number": "555-567-8901",
                "emergency_contact": "Susan Brown (555-543-2109)",
                "allergies": ["Shellfish"],
                "medications": ["Lisinopril"],
                "treatments": [],
                "consultation_history": [],
                "prescriptions": []
            }
        ]
        result = users_collection.insert_many(users_data)
        print("Users seeded.")
        inserted_users = list(users_collection.find({"_id": {"$in": result.inserted_ids}}))
        
        seeded_users = {
            "admin": [user for user in inserted_users if user["role"] == "admin"],
            "specialists": [user for user in inserted_users if user["role"] == "specialist"],
            "patients": [user for user in inserted_users if user["role"] == "patient"],
        }
        return seeded_users
    else:
        print("Users collection is not empty. Skipping seeding.")
        return {
            "admin": list(users_collection.find({"role": "admin"})),
            "specialists": list(users_collection.find({"role": "specialist"})),
            "patients": list(users_collection.find({"role": "patient"})),
        }

def seed_diagnoses(patients, specialists):
    """
    Seeds the database with initial diagnosis data.
    """
    if diagnoses_collection.count_documents({}) == 0:
        print("Seeding diagnoses...")
        diagnoses_data = []
        for i in range(len(patients)):
            patient = patients[i]
            specialist = specialists[i % len(specialists)]
            diagnoses_data.append({
                "condition_name": f"Condition {i+1}",
                "patient_id": patient["_id"],
                "specialist_id": specialist["_id"],
                "diagnosed_at": date.today() - timedelta(days=random.randint(30, 365)),
                "symptoms": ["Fever", "Cough", "Fatigue"],
                "observations": f"Patient {patient["full_name"]} presented with symptoms of Condition {i+1}.",
                "status": "active"
            })
        result = diagnoses_collection.insert_many(diagnoses_data)
        print("Diagnoses seeded.")
        return list(diagnoses_collection.find({"_id": {"$in": result.inserted_ids}}))
    else:
        print("Diagnoses collection is not empty. Skipping seeding.")
        return list(diagnoses_collection.find({}))

def seed_prescriptions(patients, specialists):
    """
    Seeds the database with initial prescription data.
    """
    if prescriptions_collection.count_documents({}) == 0:
        print("Seeding prescriptions...")
        prescriptions_data = []
        medications = ["Amoxicillin", "Ibuprofen", "Lisinopril", "Metformin", "Loratadine"]
        dosages = ["250mg", "200mg", "10mg", "500mg", "10mg"]
        frequencies = ["once_daily", "twice_daily", "three_times_daily", "as_needed"]

        for i in range(len(patients)):
            patient = patients[i]
            specialist = specialists[i % len(specialists)]
            prescriptions_data.append({
                "medication_name": random.choice(medications),
                "dosage": random.choice(dosages),
                "route": "oral",
                "frequency": random.choice(frequencies),
                "start_date": datetime.combine(date.today() - timedelta(days=random.randint(7, 60)), datetime.min.time()).date(),
                "end_date": datetime.combine(date.today() + timedelta(days=random.randint(30, 90)), datetime.min.time()).date(),
                "notes": f"Prescription for {patient["full_name"]}.",
                "prescribed_by": specialist["_id"],
                "prescribed_to": patient["_id"],
            })
        result = prescriptions_collection.insert_many(prescriptions_data)
        print("Prescriptions seeded.")
        return list(prescriptions_collection.find({"_id": {"$in": result.inserted_ids}}))
    else:
        print("Prescriptions collection is not empty. Skipping seeding.")
        return list(prescriptions_collection.find({}))

def seed_treatments(patients, specialists, prescriptions):
    """
    Seeds the database with initial treatment data.
    """
    if treatments_collection.count_documents({}) == 0:
        print("Seeding treatments...")
        treatments_data = []
        treatment_types = ["Physical Therapy", "Surgery", "Medication Management", "Counseling"]
        treatment_names = ["Knee Rehabilitation", "Appendectomy", "Diabetes Management", "Anxiety Therapy"]

        for i in range(len(patients)):
            patient = patients[i]
            specialist = specialists[i % len(specialists)]
            # Link a random prescription if available
            linked_prescriptions = [random.choice(prescriptions)["_id"]] if prescriptions else []

            treatments_data.append({
                "name": random.choice(treatment_names),
                "description": f"Treatment for {patient["full_name"]}'s condition.",
                "observations": "Patient is responding well to treatment.",
                "type": random.choice(treatment_types),
                "prescribed_by": specialist["_id"],
                "prescribed_to": patient["_id"],
                "prescriptions": linked_prescriptions,
                "status": "ongoing",
                "start_date": datetime.combine(date.today() - timedelta(days=random.randint(60, 180)), datetime.min.time()).date(),
                "end_date": datetime.combine(date.today() + timedelta(days=random.randint(30, 90)), datetime.min.time()),
                "outcome": None
            })
        result = treatments_collection.insert_many(treatments_data)
        print("Treatments seeded.")
        return list(treatments_collection.find({"_id": {"$in": result.inserted_ids}}))
    else:
        print("Treatments collection is not empty. Skipping seeding.")
        return list(treatments_collection.find({}))

def seed_appointments(patients, specialists):
    """
    Seeds the database with initial appointment data.
    """
    if appointments_collection.count_documents({}) == 0:
        print("Seeding appointments...")
        appointments_data = []
        locations = ["Clinic Room 1", "Online Consultation", "Hospital Ward A"]
        reasons = ["Follow-up", "New symptoms", "Routine check-up", "Medication review"]

        for i in range(len(patients)):
            patient = patients[i]
            specialist = specialists[i % len(specialists)]
            appointments_data.append({
                "date": datetime.utcnow() + timedelta(days=random.randint(-30, 30), hours=random.randint(9, 17)),
                "specialist_id": specialist["_id"],
                "patient_id": patient["_id"],
                "reason": random.choice(reasons),
                "notes": f"Appointment notes for {patient["full_name"]}.",
                "location": random.choice(locations),
                "status": random.choice(["scheduled", "completed"])
            })
        result = appointments_collection.insert_many(appointments_data)
        print("Appointments seeded.")
        return list(appointments_collection.find({"_id": {"$in": result.inserted_ids}}))
    else:
        print("Appointments collection is not empty. Skipping seeding.")
        return list(appointments_collection.find({}))

def seed_consultations(patients, specialists, diagnoses, treatments, appointments):
    """
    Seeds the database with initial consultation data.
    """
    if consultations_collection.count_documents({}) == 0:
        print("Seeding consultations...")
        consultations_data = []

        for i in range(len(patients)):
            patient = patients[i]
            specialist = specialists[i % len(specialists)]
            # Link a random diagnosis, treatment, and appointment if available
            linked_diagnosis = random.choice(diagnoses)["_id"] if diagnoses else None
            linked_treatments = [random.choice(treatments)["_id"]] if treatments else []
            linked_appointment = random.choice(appointments)["_id"] if appointments else None

            consultations_data.append({
                "date": datetime.combine(date.today() - timedelta(days=random.randint(1, 30)), datetime.min.time()),
                "specialist_id": specialist["_id"],
                "patient_id": patient["_id"],
                "reason": "General check-up and discussion of symptoms.",
                "notes": f"Consultation notes for {patient["full_name"]}.",
                "diagnosis": linked_diagnosis,
                "follow_up_required": random.choice([True, False]),
                "treatments": linked_treatments,
                "appointment_id": linked_appointment,
            })
        result = consultations_collection.insert_many(consultations_data)
        print("Consultations seeded.")
        return list(consultations_collection.find({"_id": {"$in": result.inserted_ids}}))
    else:
        print("Consultations collection is not empty. Skipping seeding.")
        return list(consultations_collection.find({}))

def seed_db():
    """
    Main seeder function to seed all data.
    """
    # Check if any collection has data. If so, skip seeding.
    collections_to_check = [
        users_collection,
        diagnoses_collection,
        prescriptions_collection,
        treatments_collection,
        appointments_collection,
        consultations_collection,
    ]
    
    for collection in collections_to_check:
        if collection.count_documents({}) > 0:
            print("Database is not empty. Skipping seeding.")
            return

    # If all collections are empty, proceed with seeding
    seeded_users = seed_users()
    patients = seeded_users["patients"]
    specialists = seeded_users["specialists"]

    seeded_diagnoses = seed_diagnoses(patients, specialists)
    seeded_prescriptions = seed_prescriptions(patients, specialists)
    seeded_treatments = seed_treatments(patients, specialists, seeded_prescriptions)
    seeded_appointments = seed_appointments(patients, specialists)
    seed_consultations(patients, specialists, seeded_diagnoses, seeded_treatments, seeded_appointments)