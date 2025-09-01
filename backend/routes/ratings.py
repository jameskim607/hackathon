# backend/app/routes/ratings.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, auth
from ..database import get_db

router = APIRouter()

@router.post("/", response_model=schemas.Rating)
def create_rating(
    rating: schemas.RatingCreate,
    current_user: schemas.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check if resource exists
    resource = db.query(models.Resource).filter(models.Resource.id == rating.resource_id).first()
    if resource is None:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    # Check if user has already rated this resource
    existing_rating = db.query(models.Rating).filter(
        models.Rating.resource_id == rating.resource_id,
        models.Rating.user_id == current_user.id
    ).first()
    
    if existing_rating:
        # Update existing rating
        existing_rating.rating = rating.rating
        existing_rating.review = rating.review
    else:
        # Create new rating
        db_rating = models.Rating(
            resource_id=rating.resource_id,
            user_id=current_user.id,
            rating=rating.rating,
            review=rating.review
        )
        db.add(db_rating)
    
    db.commit()
    
    if existing_rating:
        db.refresh(existing_rating)
        return existing_rating
    else:
        db.refresh(db_rating)
        return db_rating

@router.get("/resource/{resource_id}", response_model=List[schemas.Rating])
def get_ratings_for_resource(resource_id: int, db: Session = Depends(get_db)):
    ratings = db.query(models.Rating).filter(models.Rating.resource_id == resource_id).all()
    return ratings

@router.get("/{rating_id}", response_model=schemas.Rating)
def get_rating(rating_id: int, db: Session = Depends(get_db)):
    rating = db.query(models.Rating).filter(models.Rating.id == rating_id).first()
    if rating is None:
        raise HTTPException(status_code=404, detail="Rating not found")
    return rating