# backend/app/routes/translations.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, auth, ai_services
from ..database import get_db

router = APIRouter()

@router.post("/", response_model=schemas.Translation)
def create_translation(
    translation: schemas.TranslationCreate,
    current_user: schemas.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check if resource exists
    resource = db.query(models.Resource).filter(models.Resource.id == translation.resource_id).first()
    if resource is None:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    # Use AI service to translate content
    translated_title = translation.translated_title
    if not translated_title:
        translated_title = ai_services.translate_text(resource.title, translation.language)
    
    translated_description = translation.translated_description
    if not translated_description and resource.description:
        translated_description = ai_services.translate_text(resource.description, translation.language)
    
    # For text resources, translate the content
    translated_content = translation.translated_content
    if not translated_content and resource.file_type == models.FileType.text and resource.file_path:
        # Read the text file and translate it
        try:
            with open(resource.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            translated_content = ai_services.translate_text(content, translation.language)
        except:
            pass  # If translation fails, keep the original content
    
    # Create translation
    db_translation = models.Translation(
        resource_id=translation.resource_id,
        language=translation.language,
        translated_title=translated_title,
        translated_description=translated_description,
        translated_content=translated_content
    )
    
    db.add(db_translation)
    db.commit()
    db.refresh(db_translation)
    
    return db_translation

@router.get("/resource/{resource_id}", response_model=List[schemas.Translation])
def get_translations_for_resource(resource_id: int, db: Session = Depends(get_db)):
    translations = db.query(models.Translation).filter(
        models.Translation.resource_id == resource_id
    ).all()
    return translations

@router.get("/{translation_id}", response_model=schemas.Translation)
def get_translation(translation_id: int, db: Session = Depends(get_db)):
    translation = db.query(models.Translation).filter(models.Translation.id == translation_id).first()
    if translation is None:
        raise HTTPException(status_code=404, detail="Translation not found")
    return translation