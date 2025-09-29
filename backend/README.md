
# Healthy.me API Documentation

## About the Project

This project is a FastAPI-based backend for a medical application called "Healthy.me". It provides a comprehensive API for managing patients, specialists, appointments, consultations, diagnoses, and treatments. The application is designed to be used by patients, specialists, and administrators, with different levels of access and permissions for each role.

## Technologies

The project is built with Python and leverages the following key technologies and libraries:

-   **FastAPI**: A modern, fast (high-performance) web framework for building APIs with Python 3.7+ based on standard Python type hints.
-   **MongoDB**: A NoSQL database used for storing all the application data.
-   **Pydantic**: A data validation and settings management library using Python type annotations.
-   **JWT (JSON Web Tokens)**: For securing the API and authenticating users.
-   **Passlib**: A password hashing library for securely storing user passwords.
-   **Uvicorn**: An ASGI server for running the FastAPI application.
-   **bcrypt**: A password-hashing function.
-   **python-dotenv**: For managing environment variables.
-   **python-multipart**: For handling file uploads.

## App's Workflow

The application follows a typical client-server architecture. The frontend (not included in this project) interacts with the backend through the API endpoints. The workflow can be summarized as follows:

1.  **User Registration**: New users can register as either a "patient" or a "specialist". The registration process includes password validation and hashing for security.
2.  **Authentication**: Registered users can log in to the application using their credentials. Upon successful login, the server generates a JWT token that must be included in the headers of subsequent requests to access protected endpoints.
3.  **User Roles and Permissions**: The application has three user roles: "patient", "specialist", and "admin". Each role has different permissions and access levels to the API endpoints.
    -   **Patients**: Can manage their own profile, search for specialists, book appointments, and view their medical history (consultations, diagnoses, and treatments).
    -   **Specialists**: Can manage their own profile, view their assigned patients, manage appointments, and create and manage consultations, diagnoses, and treatments for their patients.
    -   **Admins**: Have full access to the application and can manage all users, appointments, and other data.
4.  **Data Management**: The application provides a set of API endpoints for managing the following data:
    -   **Users**: Create, read, update, and delete users.
    -   **Patients**: Manage patient profiles and medical records.
    -   **Specialists**: Manage specialist profiles and patient lists.
    -   **Appointments**: Create, confirm, and manage appointments.
    -   **Consultations**: Create and manage consultations, including diagnoses and treatments.
    -   **Diagnoses**: Create, read, update, and delete diagnoses.
    -   **Treatments**: Create, read, update, and delete treatments.

## API Endpoints

The API is organized into several routers, each responsible for a specific resource. The following is a detailed description of each endpoint:

### Auth

-   **`POST /auth/register`**: Registers a new patient.
-   **`POST /auth/register/specialist`**: Registers a new specialist.
-   **`POST /auth/login`**: Authenticates a user and returns a JWT token.
-   **`GET /auth/me`**: Returns the current user's information.
-   **`PUT /auth/toggle-admin/{user_id}`**: Toggles the admin role of a user (admin only).

### Users

-   **`GET /users`**: Returns a list of all users (admin only).
-   **`GET /users/search`**: Searches for users based on various criteria (admin only).
-   **`GET /users/{user_id}`**: Returns a specific user by ID.
-   **`POST /users`**: Creates a new user (admin only).
-   **`DELETE /users/{user_id}`**: Deletes a user by ID (admin or the user themselves).

### Patients

-   **`GET /patients`**: Returns a list of patients (admins see all, specialists see their own).
-   **`GET /patients/search`**: Searches for patients (admins see all, specialists see their own).
-   **`GET /patients/{patient_id}`**: Returns a specific patient by ID (the patient themselves, their specialist, or an admin).
-   **`PUT /patients/me`**: Updates the current patient's information.
-   **`DELETE /patients/{patient_id}`**: Deletes a patient by ID (the patient themselves or an admin).

### Specialists

-   **`GET /specialists`**: Returns a list of all specialists.
-   **`GET /specialists/search`**: Searches for specialists based on various criteria.
-   **`GET /specialists/{specialist_id}`**: Returns a specific specialist by ID.
-   **`PUT /specialists/me`**: Updates the current specialist's information.
-   **`POST /specialists/me/patients`**: Adds a patient to the current specialist's list using the patient's unique code.
-   **`DELETE /specialists/me/patients/{patient_id}`**: Removes a patient from the current specialist's patient list.
-   **`DELETE /specialists/{specialist_id}`**: Deletes a specialist by ID (the specialist themselves or an admin).

### Appointments

-   **`POST /appointments`**: Creates a new appointment or appointment request.
-   **`POST /appointments/{appointment_id}/confirm`**: Confirms a pending appointment (specialist only).
-   **`GET /appointments/search`**: Searches for appointments based on various criteria.
-   **`GET /appointments`**: Lists all appointments with pagination.
-   **`GET /appointments/{appointment_id}`**: Gets a specific appointment by ID.
-   **`PUT /appointments/{appointment_id}`**: Updates an existing appointment.

### Consultations

-   **`POST /consultations`**: Creates a new consultation (specialist only).
-   **`GET /consultations/search`**: Searches for consultations based on various criteria.
-   **`GET /consultations`**: Lists all consultations with pagination.
-   **`GET /consultations/{consultation_id}`**: Gets a specific consultation by ID.

### Diagnoses

-   **`POST /diagnoses`**: Creates a new diagnosis (specialist only).
-   **`GET /diagnoses/by-patient/{patient_id}`**: Gets all diagnoses for a specific patient.
-   **`GET /diagnoses/{diagnosis_id}`**: Gets a specific diagnosis by ID.
-   **`PUT /diagnoses/{diagnosis_id}`**: Updates an existing diagnosis.
-   **`DELETE /diagnoses/{diagnosis_id}`**: Deletes a diagnosis by ID.

### Treatments

-   **`POST /treatments`**: Creates a new treatment (specialist only).
-   **`GET /treatments`**: Lists all treatments with pagination.
-   **`GET /treatments/{treatment_id}`**: Gets a specific treatment by ID.
-   **`PUT /treatments/{treatment_id}`**: Updates an existing treatment.
-   **`DELETE /treatments/{treatment_id}`**: Deletes a treatment by ID.
