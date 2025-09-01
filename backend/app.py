# app.py
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import enum
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os

# Database setup - using SQLite for simplicity (no MySQL needed)
SQLALCHEMY_DATABASE_URL = "sqlite:///./african_lms.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = "your-secret-key-here-change-in-production"
ALGORITHM = "HS256"

# Enums
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

# Database Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default=UserRole.student.value)
    phone_number = Column(String(20))
    country = Column(String(50))
    language_preference = Column(String(10), default="en")
    is_teacher_verified = Column(Boolean, default=False)

class Resource(Base):
    __tablename__ = "resources"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    file_path = Column(String(255))
    file_type = Column(String(20), nullable=False)
    subject = Column(String(100), nullable=False)
    grade_level = Column(String(50), nullable=False)
    country = Column(String(50), nullable=False)
    language = Column(String(10), default="en")
    tags = Column(Text)
    uploaded_by = Column(Integer, nullable=False)
    is_approved = Column(Boolean, default=False)
    view_count = Column(Integer, default=0)

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic Models
class UserBase(BaseModel):
    username: str
    email: str
    role: UserRole = UserRole.student
    phone_number: Optional[str] = None
    country: Optional[str] = None
    language_preference: str = "en"

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_teacher_verified: bool

    class Config:
        from_attributes = True

class ResourceBase(BaseModel):
    title: str
    description: Optional[str] = None
    file_type: FileType
    subject: str
    grade_level: str
    country: str
    language: str = "en"
    tags: Optional[str] = None

class ResourceResponse(ResourceBase):
    id: int
    uploaded_by: int
    is_approved: bool
    view_count: int
    file_path: Optional[str] = None

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# FastAPI App
app = FastAPI(title="African LMS API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Auth functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user

def create_access_token(data: dict):
    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# OAuth2 scheme for token
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

# Routes
@app.post("/api/v1/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    db_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()
    
    if db_user:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    
    # Create user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password,
        role=user.role.value,
        phone_number=user.phone_number,
        country=user.country,
        language_preference=user.language_preference,
        is_teacher_verified=(user.role == UserRole.admin)  # Auto-verify admins
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@app.post("/api/v1/users/login")
def login(login_request: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, login_request.username, login_request.password)
    if not user:
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

@app.get("/api/v1/resources/", response_model=List[ResourceResponse])
def get_resources(
    skip: int = 0,
    limit: int = 100,
    subject: Optional[str] = None,
    grade_level: Optional[str] = None,
    country: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Resource).filter(Resource.is_approved == True)
    
    if subject:
        query = query.filter(Resource.subject.ilike(f"%{subject}%"))
    if grade_level:
        query = query.filter(Resource.grade_level.ilike(f"%{grade_level}%"))
    if country:
        query = query.filter(Resource.country.ilike(f"%{country}%"))
    
    resources = query.offset(skip).limit(limit).all()
    return resources

@app.get("/")
def read_root():
    return {"message": "Welcome to African LMS API"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "SQLite"}

@app.get("/test-data")
def test_data(db: Session = Depends(get_db)):
    # Create test data
    test_user = User(
        username="testuser",
        email="test@example.com",
        password_hash=get_password_hash("test123"),
        role="student",
        is_teacher_verified=True
    )
    
    db.add(test_user)
    db.commit()
    
    test_resource = Resource(
        title="Mathematics Basics",
        description="Introduction to basic mathematics",
        file_type="pdf",
        subject="Mathematics",
        grade_level="Primary",
        country="Nigeria",
        uploaded_by=test_user.id,
        is_approved=True
    )
    
    db.add(test_resource)
    db.commit()
    
    return {"message": "Test data created", "user_id": test_user.id, "resource_id": test_resource.id}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)