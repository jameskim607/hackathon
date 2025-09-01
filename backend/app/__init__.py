# backend/app/__init__.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routes import users, resources, translations, ratings

# Create database tables
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

# Include routers
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(resources.router, prefix="/api/v1/resources", tags=["resources"])
app.include_router(translations.router, prefix="/api/v1/translations", tags=["translations"])
app.include_router(ratings.router, prefix="/api/v1/ratings", tags=["ratings"])

@app.get("/")
def read_root():
    return {"message": "Welcome to African LMS API"}