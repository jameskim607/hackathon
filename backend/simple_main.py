# backend/simple_main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os

app = FastAPI(title="African LMS API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple models for testing
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str = "student"

class LoginRequest(BaseModel):
    username: str
    password: str

# Mock data for testing
mock_users = [
    {"id": 1, "username": "admin", "email": "admin@example.com", "role": "admin", "password": "admin123"},
    {"id": 2, "username": "teacher1", "email": "teacher@example.com", "role": "teacher", "password": "teacher123"},
    {"id": 3, "username": "student1", "email": "student@example.com", "role": "student", "password": "student123"}
]

mock_resources = [
    {"id": 1, "title": "Mathematics Basics", "subject": "Mathematics", "grade_level": "Primary", "country": "Nigeria"},
    {"id": 2, "title": "Science Introduction", "subject": "Science", "grade_level": "Secondary", "country": "Kenya"},
    {"id": 3, "title": "English Grammar", "subject": "Languages", "grade_level": "Primary", "country": "Ghana"}
]

# Simple endpoints for testing
@app.get("/")
def read_root():
    return {"message": "Welcome to African LMS API"}

@app.post("/api/v1/users/")
def create_user(user: UserCreate):
    # Check if user already exists
    for u in mock_users:
        if u["username"] == user.username or u["email"] == user.email:
            raise HTTPException(status_code=400, detail="Username or email already exists")
    
    # Create new user (in real app, hash the password)
    new_user = {
        "id": len(mock_users) + 1,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "password": user.password  # In real app, hash this
    }
    mock_users.append(new_user)
    return new_user

@app.post("/api/v1/users/login")
def login(login_request: LoginRequest):
    for user in mock_users:
        if user["username"] == login_request.username and user["password"] == login_request.password:
            return {"access_token": f"mock_token_{user['id']}", "token_type": "bearer", "user": user}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/api/v1/resources/")
def get_resources(subject: Optional[str] = None, grade_level: Optional[str] = None, country: Optional[str] = None):
    filtered_resources = mock_resources
    if subject:
        filtered_resources = [r for r in filtered_resources if r["subject"].lower() == subject.lower()]
    if grade_level:
        filtered_resources = [r for r in filtered_resources if r["grade_level"].lower() == grade_level.lower()]
    if country:
        filtered_resources = [r for r in filtered_resources if r["country"].lower() == country.lower()]
    return filtered_resources

@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "mock_data"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)