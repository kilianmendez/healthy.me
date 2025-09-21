# Healthy.me - Backend

This repository contains the backend service for **Healthy.me**, a comprehensive platform designed to connect patients with medical specialists. It handles user management, appointment scheduling, consultations, and medical record-keeping.

The application is built with Python using the FastAPI framework, ensuring high performance and a robust API.

## Features

- **User Authentication**: Secure user registration and login using JWT tokens.
- **Role-Based Access**: Differentiated access and functionalities for Patients and Specialists.
- **Appointment Management**: Schedule, view, and manage medical appointments.
- **Consultation Tracking**: Create and manage records for each medical consultation.
- **Medical Records**: Handle diagnoses, treatments, and prescriptions associated with consultations.
- **Profile Management**: Users can manage their profiles, including uploading avatars.

## Technology Stack

- **Python 3.12**
- **FastAPI**: For building the RESTful API.
- **Pydantic**: For data validation and settings management.
- **MongoDB**: As the database for the application.
- **Motor**: Asynchronous Python driver for MongoDB.
- **Uvicorn**: As the ASGI server to run the application.
- **JWT**: For handling authentication tokens.

## Project Structure

The project is organized into the following directories:

```
/app
├── /db           # Database client, connection, and ORM models.
├── /routers      # API endpoint definitions for each resource (users, appointments, etc.).
├── /schemas      # Pydantic models for request/response data validation.
├── /utils        # Utility functions, including security and other helpers.
├── /uploads      # Directory for storing user-uploaded files (e.g., avatars).
└── main.py       # Main application entry point where the FastAPI app is initialized.
```

## API Endpoints

The API is structured around REST principles. Here are the main resources:

- `/auth`: Handles user registration and login (token generation).
- `/users`: General user management.
- `/patients`: Patient-specific data and operations.
- `/specialists`: Specialist-specific data and operations.
- `/appointments`: For creating, retrieving, and managing appointments.
- `/consultations`: Manages consultation records.
- `/diagnoses`: Manages diagnoses linked to consultations.
- `/treatments`: Manages treatments linked to consultations.
- `/prescriptions`: Manages prescriptions linked to consultations.

## Getting Started

To get the application running locally, follow these steps.

### 1. Prerequisites

- Python 3.10+
- A package manager like `pip`.

### 2. Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/healthy.me.git
    cd healthy.me/backend
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # For Windows
    python -m venv venv
    .\venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    *(Note: A `requirements.txt` file is recommended. If it doesn't exist, you can create one using `pip freeze > requirements.txt` after installing the necessary packages.)*
    ```bash
    pip install -r requirements.txt
    ```

### 3. Configuration

1.  Create a `.env` file in the `app` directory by copying the example or creating it from scratch.
2.  Add the necessary environment variables. At a minimum, you will likely need:
    ```
    DATABASE_URL="mongodb://user:password@host:port/database_name"
    SECRET_KEY="your_super_secret_key"
    ALGORITHM="HS256"
    ```

### 4. Running the Application

Once the setup is complete, you can run the application using Uvicorn:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000` and the interactive documentation (Swagger UI) at `http://127.0.0.1:8000/docs`.

