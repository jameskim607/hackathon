from fastapi import FastAPI, HTTPException, Depends, status, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional
import os
import shutil

from .database import SessionLocal, engine, Base
from . import models, schemas
from .auth import get_password_hash, verify_password, create_access_token, SECRET_KEY, ALGORITHM, oauth2_scheme, get_current_user

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="African LMS API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Routes
@app.post("/api/v1/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    db_user = db.query(models.User).filter(
        (models.User.username == user.username) | 
        (models.User.email == user.email)
    ).first()
    
    if db_user:
        raise HTTPException(status_code=400, detail="Username or email already registered")
    
    # Hash password and create user
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password,
        role=user.role,
        phone_number=user.phone_number,
        country=user.country,
        language_preference=user.language_preference,
        is_teacher_verified=(user.role == schemas.UserRole.admin)
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/api/v1/users/login")
def login(login_request: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == login_request.username).first()
    
    if not user or not verify_password(login_request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user.username})
    
    return {
        "access_token": access_token, 
        "token_type": "bearer", 
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "is_teacher_verified": user.is_teacher_verified
        }
    }

@app.get("/api/v1/resources/", response_model=List[schemas.Resource])
def get_resources(
    skip: int = 0,
    limit: int = 100,
    subject: Optional[str] = None,
    grade_level: Optional[str] = None,
    country: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Resource).filter(models.Resource.is_approved == True)
    
    if subject:
        query = query.filter(models.Resource.subject.ilike(f"%{subject}%"))
    if grade_level:
        query = query.filter(models.Resource.grade_level.ilike(f"%{grade_level}%"))
    if country:
        query = query.filter(models.Resource.country.ilike(f"%{country}%"))
    
    return query.offset(skip).limit(limit).all()

@app.post("/api/v1/resources/", response_model=schemas.Resource)
def create_resource(
    title: str = Form(...),
    description: str = Form(...),
    file_type: str = Form(...),
    subject: str = Form(...),
    grade_level: str = Form(...),
    country: str = Form(...),
    language: str = Form(default="en"),
    tags: str = Form(default=""),
    file: UploadFile = File(...),
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "teacher" and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only teachers can upload resources")
    
    # Save file
    os.makedirs("uploads", exist_ok=True)
    file_location = f"uploads/{file.filename}"
    
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Create resource
    db_resource = models.Resource(
        title=title,
        description=description,
        file_path=file_location,
        file_type=file_type,
        subject=subject,
        grade_level=grade_level,
        country=country,
        language=language,
        tags=tags,
        uploaded_by=current_user.id,
        is_approved=(current_user.role == "admin")
    )
    
    db.add(db_resource)
    db.commit()
    db.refresh(db_resource)
    return db_resource

@app.get("/")
def read_root():
    return {"message": "Welcome to African LMS API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}