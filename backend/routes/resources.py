# backend/app/routes/resources.py
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import models, schemas, auth
from ..database import get_db
import os
import shutil

router = APIRouter()

# Ensure upload directory exists
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/", response_model=schemas.Resource)
def create_resource(
    resource: schemas.ResourceCreate,
    file: Optional[UploadFile] = File(None),
    current_user: schemas.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check if user is a teacher
    if current_user.role != schemas.UserRole.teacher and current_user.role != schemas.UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only teachers can upload resources"
        )
    
    # Check if teacher is verified
    if current_user.role == schemas.UserRole.teacher and not current_user.is_teacher_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Teacher account not verified"
        )
    
    file_path = None
    if file:
        # Save uploaded file
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    
    # Create resource
    db_resource = models.Resource(
        title=resource.title,
        description=resource.description,
        file_path=file_path,
        file_type=resource.file_type,
        subject=resource.subject,
        grade_level=resource.grade_level,
        country=resource.country,
        language=resource.language,
        tags=resource.tags,
        uploaded_by=current_user.id,
        is_approved=(current_user.role == schemas.UserRole.admin)  # Auto-approve for admins
    )
    
    db.add(db_resource)
    db.commit()
    db.refresh(db_resource)
    
    return db_resource

@router.get("/", response_model=List[schemas.Resource])
def read_resources(
    skip: int = 0,
    limit: int = 100,
    subject: Optional[str] = None,
    grade_level: Optional[str] = None,
    country: Optional[str] = None,
    language: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Resource).filter(models.Resource.is_approved == True)
    
    if subject:
        query = query.filter(models.Resource.subject == subject)
    if grade_level:
        query = query.filter(models.Resource.grade_level == grade_level)
    if country:
        query = query.filter(models.Resource.country == country)
    if language:
        query = query.filter(models.Resource.language == language)
    
    resources = query.offset(skip).limit(limit).all()
    return resources

@router.get("/{resource_id}", response_model=schemas.Resource)
def read_resource(resource_id: int, db: Session = Depends(get_db)):
    resource = db.query(models.Resource).filter(models.Resource.id == resource_id).first()
    if resource is None:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    # Increment view count
    resource.view_count += 1
    db.commit()
    db.refresh(resource)
    
    return resource

@router.put("/{resource_id}/approve", response_model=schemas.Resource)
def approve_resource(
    resource_id: int,
    current_user: schemas.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    # Only admins can approve resources
    if current_user.role != schemas.UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can approve resources"
        )
    
    resource = db.query(models.Resource).filter(models.Resource.id == resource_id).first()
    if resource is None:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    resource.is_approved = True
    db.commit()
    db.refresh(resource)
    
    return resource