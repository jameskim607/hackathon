# backend/app/models.py
from sqlalchemy import Column, Integer, String, Text, Boolean, Enum, ForeignKey, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base
import enum

class UserRole(str, enum.Enum):
    admin = "admin"
    teacher = "teacher"
    student = "student"

class FileType(str, enum.Enum):
    pdf = "pdf"
    video = "video"
    text = "text"
    slides = "slides"
    link = "link"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.student)
    phone_number = Column(String(20))
    country = Column(String(50))
    language_preference = Column(String(10), default="en")
    is_teacher_verified = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    resources = relationship("Resource", back_populates="uploader")
    ratings = relationship("Rating", back_populates="user")

class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    file_path = Column(String(255))
    file_type = Column(Enum(FileType), nullable=False)
    subject = Column(String(100), nullable=False)
    grade_level = Column(String(50), nullable=False)
    country = Column(String(50), nullable=False)
    language = Column(String(10), default="en")
    tags = Column(Text)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    upload_date = Column(TIMESTAMP, server_default=func.now())
    is_approved = Column(Boolean, default=False)
    view_count = Column(Integer, default=0)
    
    uploader = relationship("User", back_populates="resources")
    translations = relationship("Translation", back_populates="resource")
    ratings = relationship("Rating", back_populates="resource")
    tts = relationship("TextToSpeech", back_populates="resource")
    summaries = relationship("Summary", back_populates="resource")

class Translation(Base):
    __tablename__ = "translations"

    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(Integer, ForeignKey("resources.id"), nullable=False)
    language = Column(String(10), nullable=False)
    translated_title = Column(String(255))
    translated_description = Column(Text)
    translated_content = Column(Text)
    translation_date = Column(TIMESTAMP, server_default=func.now())
    
    resource = relationship("Resource", back_populates="translations")

class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(Integer, ForeignKey("resources.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rating = Column(Integer)
    review = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    resource = relationship("Resource", back_populates="ratings")
    user = relationship("User", back_populates="ratings")

class TextToSpeech(Base):
    __tablename__ = "text_to_speech"

    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(Integer, ForeignKey("resources.id"), nullable=False)
    language = Column(String(10), nullable=False)
    audio_path = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    resource = relationship("Resource", back_populates="tts")

class Summary(Base):
    __tablename__ = "summaries"

    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(Integer, ForeignKey("resources.id"), nullable=False)
    language = Column(String(10), nullable=False)
    summary_text = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    resource = relationship("Resource", back_populates="summaries")

class USSDSession(Base):
    __tablename__ = "ussd_sessions"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(20), nullable=False)
    session_id = Column(String(100), nullable=False)
    menu_level = Column(String(50), default="main")
    selected_subject = Column(String(100))
    selected_grade = Column(String(50))
    selected_resource_id = Column(Integer)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())