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

    # --- Realistic Data Pools ---
    first_names_male = ["John", "Michael", "David", "James", "Robert", "William", "Richard", "Joseph", "Thomas", "Charles"]
    first_names_female = ["Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Susan", "Jessica", "Sarah", "Karen", "Nancy"]
    last_names = ["Smith", "Jones", "Williams", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin", "Thompson", "Garcia", "Martinez", "Robinson", "Clark"]
    
    genders = [Gender.male.value, Gender.female.value]

    patient_allergies = ["Pollen", "Dust Mites", "Peanuts", "Penicillin", "Latex", "Cats", "Dogs", "Shellfish", "Sulfites", "Bee Stings"]
    patient_medications = ["Aspirin", "Ibuprofen", "Amoxicillin", "Lisinopril", "Metformin", "Levothyroxine", "Atorvastatin", "Gabapentin", "Hydrochlorothiazide", "Sertraline"]

    specialties_list = [
        "Cardiology", "Dermatology", "Pediatrics", "Neurology", "Orthopedics",
        "Oncology", "Psychiatry", "Gastroenterology", "Endocrinology", "Ophthalmology",
        "General Practice", "Internal Medicine", "Pulmonology", "Urology", "Nephrology",
        "Rheumatology", "Infectious Disease", "Allergy and Immunology", "Emergency Medicine", "Anesthesiology"
    ]
    workplaces_list = [
        "City General Hospital", "Downtown Medical Clinic", "Specialty Care Center",
        "University Health System", "Community Family Practice", "Advanced Diagnostics Lab",
        "Regional Medical Center", "St. Jude's Hospital", "Green Valley Clinic", "Coastal Health Group"
    ]
    biography_templates = [
        "{name} is a dedicated {specialty} with over {years} years of experience. Passionate about patient-centered care and innovative treatments.",
        "A compassionate {specialty} specialist, Dr. {name} focuses on holistic health and preventive medicine, ensuring comprehensive care for all patients.",
        "With a strong background in {specialty}, Dr. {name} is committed to providing personalized and effective medical solutions, utilizing the latest research and technology.",
        "Expert in {specialty}, Dr. {name} is known for their empathetic approach and ability to connect with patients, making complex medical information easy to understand.",
        "{name} brings {years} years of expertise in {specialty}, offering advanced diagnostic and treatment options to improve patient outcomes."
    ]
    certification_templates = [
        "Board Certified in {specialty}",
        "Fellow of the American College of {specialty_short}",
        "Certified by the {organization} in {specialty}",
        "Diplomate of the American Board of {specialty}"
    ]
    organizations = ["Medical Association", "Specialty Board", "Physician's Guild"]
    # --- End Data Pools ---

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

    # Patients
    patients_data = []
    for i in range(1, 6):
        gender_choice = random.choice(genders)
        fname = random.choice(first_names_male) if gender_choice == Gender.male.value else random.choice(first_names_female)
        lname = random.choice(last_names)
        full_name = f"{fname} {lname}"
        username = f"{fname.lower()}{lname.lower()}{i}"
        
        patient_password_raw = f"{username.capitalize()}@1234"
        patient_password_hashed = get_password_hash(patient_password_raw)

        dob_year = random.randint(1960, 2005)
        dob_month = random.randint(1, 12)
        dob_day = random.randint(1, 28)
        
        patients_data.append({
            "_id": ObjectId(),
            "username": username,
            "email": f"{username}@gmail.com",
            "password": patient_password_hashed,
            "full_name": full_name,
            "role": "patient",
            "disabled": False,
            "is_verified": True,
            "created_at": datetime.datetime.utcnow() - timedelta(days=random.randint(30, 365*5)),
            "updated_at": datetime.datetime.utcnow() - timedelta(days=random.randint(1, 30)),
            "date_of_birth": datetime.datetime.combine(date(dob_year, dob_month, dob_day), datetime.datetime.min.time()),
            "gender": gender_choice,
            "avatar_url": None,
            "phone_number": f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
            "emergency_contact": {"name": f"{random.choice(first_names_male + first_names_female)} {random.choice(last_names)}", "phone": f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"},
            "allergies": random.sample(patient_allergies, k=random.randint(0, 2)),
            "medications": random.sample(patient_medications, k=random.randint(0, 1)),
            "treatments": [],
            "consultation_history": [],
            "prescriptions": []
        })
    users_collection.insert_many(patients_data)
    print(f"{len(patients_data)} patient users created.")

    # Specialists
    specialists_data = []
    for i in range(1, 6):
        gender_choice = random.choice(genders)
        fname = random.choice(first_names_male) if gender_choice == Gender.male.value else random.choice(first_names_female)
        lname = random.choice(last_names)
        full_name = f"Dr. {fname} {lname}"
        username = f"{fname.lower()}{lname.lower()}{i}"

        specialist_password_raw = f"{username.capitalize()}@1234"
        specialist_password_hashed = get_password_hash(specialist_password_raw)

        dob_year = random.randint(1950, 1985)
        dob_month = random.randint(1, 12)
        dob_day = random.randint(1, 28)
        
        chosen_specialties = random.sample(specialties_list, k=random.randint(1, 2))
        chosen_workplaces = random.sample(workplaces_list, k=random.randint(1, 2))
        years_experience = random.randint(5, 30)

        specialists_data.append({
            "_id": ObjectId(),
            "username": username,
            "email": f"{username}@gmail.com",
            "password": specialist_password_hashed,
            "full_name": full_name,
            "role": "specialist",
            "disabled": False,
            "is_verified": True,
            "created_at": datetime.datetime.utcnow() - timedelta(days=random.randint(365*5, 365*10)),
            "updated_at": datetime.datetime.utcnow() - timedelta(days=random.randint(1, 60)),
            "date_of_birth": datetime.datetime.combine(date(dob_year, dob_month, dob_day), datetime.datetime.min.time()),
            "gender": gender_choice,
            "avatar_url": None,
            "workplaces": chosen_workplaces,
            "available_hours": f"Mon-Fri {random.randint(8, 10)}:00-{random.randint(16, 18)}:00",
            "specialties": chosen_specialties,
            "biography": random.choice(biography_templates).format(name=full_name, specialty=chosen_specialties[0], years=years_experience),
            "certifications": [random.choice(certification_templates).format(specialty=s, specialty_short=s.split()[0], organization=random.choice(organizations)) for s in chosen_specialties],
            "patients": []
        })
    users_collection.insert_many(specialists_data)
    print(f"{len(specialists_data)} specialist users created.")

    print("Database seeding complete.")
