# backend/app/schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    admin = "admin"
    teacher = "teacher"
    student = "student"

class FileType(str, Enum):
    pdf = "pdf"
    video = "video"
    text = "text"
    slides = "slides"
    link = "link"

class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: UserRole = UserRole.student
    phone_number: Optional[str] = None
    country: Optional[str] = None
    language_preference: str = "en"

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_teacher_verified: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class ResourceBase(BaseModel):
    title: str
    description: Optional[str] = None
    file_type: FileType
    subject: str
    grade_level: str
    country: str
    language: str = "en"
    tags: Optional[str] = None

class ResourceCreate(ResourceBase):
    pass

class Resource(ResourceBase):
    id: int
    uploaded_by: int
    upload_date: datetime
    is_approved: bool
    view_count: int
    file_path: Optional[str] = None

    class Config:
        orm_mode = True

class TranslationBase(BaseModel):
    language: str
    translated_title: Optional[str] = None
    translated_description: Optional[str] = None
    translated_content: Optional[str] = None

class TranslationCreate(TranslationBase):
    resource_id: int

class Translation(TranslationBase):
    id: int
    resource_id: int
    translation_date: datetime

    class Config:
        orm_mode = True

class RatingBase(BaseModel):
    rating: int
    review: Optional[str] = None

class RatingCreate(RatingBase):
    resource_id: int

class Rating(RatingBase):
    id: int
    user_id: int
    resource_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class USSDRequest(BaseModel):
    phoneNumber: str
    sessionId: str
    text: str = ""

class USSDResponse(BaseModel):
    message: str
    status: str = "200"