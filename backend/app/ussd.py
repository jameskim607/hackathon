# backend/app/ussd.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas
from .database import get_db
from .ai_services import ai_services

router = APIRouter()

@router.post("/ussd", response_model=schemas.USSDResponse)
async def handle_ussd(request: schemas.USSDRequest, db: Session = Depends(get_db)):
    text = request.text.strip()
    parts = text.split('*') if text else []
    phone_number = request.phoneNumber
    session_id = request.sessionId
    
    # Get or create USSD session
    session = db.query(models.USSDSession).filter(
        models.USSDSession.session_id == session_id
    ).first()
    
    if not session:
        session = models.USSDSession(
            phone_number=phone_number,
            session_id=session_id,
            menu_level="main"
        )
        db.add(session)
        db.commit()
        db.refresh(session)
    
    response_message = ""
    
    # Main menu
    if session.menu_level == "main":
        if not parts:
            response_message = "CON Welcome to African LMS:\n1. Browse Subjects\n2. Search Resources\n3. My Account\n0. Exit"
        else:
            choice = parts[0]
            if choice == "1":
                session.menu_level = "browse_subjects"
                db.commit()
                response_message = "CON Select Subject:\n1. Mathematics\n2. Science\n3. Languages\n4. History\n5. Geography\n0. Back"
            elif choice == "2":
                session.menu_level = "search"
                db.commit()
                response_message = "CON Enter search term:"
            elif choice == "3":
                session.menu_level = "account"
                db.commit()
                response_message = "CON Account Options:\n1. Register\n2. Login\n0. Back"
            elif choice == "0":
                response_message = "END Thank you for using African LMS"
            else:
                response_message = "CON Invalid choice. Try again:\n1. Browse Subjects\n2. Search Resources\n3. My Account\n0. Exit"
    
    # Browse subjects
    elif session.menu_level == "browse_subjects":
        if len(parts) < 2:
            response_message = "CON Select Subject:\n1. Mathematics\n2. Science\n3. Languages\n4. History\n5. Geography\n0. Back"
        else:
            choice = parts[1]
            subject_map = {
                "1": "Mathematics",
                "2": "Science",
                "3": "Languages",
                "4": "History",
                "5": "Geography"
            }
            
            if choice == "0":
                session.menu_level = "main"
                db.commit()
                response_message = "CON Welcome to African LMS:\n1. Browse Subjects\n2. Search Resources\n3. My Account\n0. Exit"
            elif choice in subject_map:
                session.selected_subject = subject_map[choice]
                session.menu_level = "select_grade"
                db.commit()
                response_message = "CON Select Grade Level:\n1. Primary\n2. Secondary\n3. University\n0. Back"
            else:
                response_message = "CON Invalid choice. Try again:\n1. Mathematics\n2. Science\n3. Languages\n4. History\n5. Geography\n0. Back"
    
    # Select grade level
    elif session.menu_level == "select_grade":
        if len(parts) < 3:
            response_message = "CON Select Grade Level:\n1. Primary\n2. Secondary\n3. University\n0. Back"
        else:
            choice = parts[2]
            grade_map = {
                "1": "Primary",
                "2": "Secondary",
                "3": "University"
            }
            
            if choice == "0":
                session.menu_level = "browse_subjects"
                session.selected_subject = None
                db.commit()
                response_message = "CON Select Subject:\n1. Mathematics\n2. Science\n3. Languages\n4. History\n5. Geography\n0. Back"
            elif choice in grade_map:
                session.selected_grade = grade_map[choice]
                session.menu_level = "browse_resources"
                db.commit()
                
                # Get resources for selected subject and grade
                resources = db.query(models.Resource).filter(
                    models.Resource.subject == session.selected_subject,
                    models.Resource.grade_level == session.selected_grade,
                    models.Resource.is_approved == True
                ).limit(5).all()
                
                if resources:
                    options = "\n".join([f"{i+1}. {r.title}" for i, r in enumerate(resources)])
                    response_message = f"CON Select Resource:\n{options}\n0. Back"
                else:
                    response_message = "CON No resources found for this criteria.\n0. Back"
            else:
                response_message = "CON Invalid choice. Try again:\n1. Primary\n2. Secondary\n3. University\n0. Back"
    
    # Browse resources
    elif session.menu_level == "browse_resources":
        if len(parts) < 4:
            # This shouldn't happen normally, but handle it
            response_message = "CON Select Resource:\n0. Back"
        else:
            choice = parts[3]
            
            if choice == "0":
                session.menu_level = "select_grade"
                session.selected_grade = None
                db.commit()
                response_message = "CON Select Grade Level:\n1. Primary\n2. Secondary\n3. University\n0. Back"
            else:
                # Get resources again
                resources = db.query(models.Resource).filter(
                    models.Resource.subject == session.selected_subject,
                    models.Resource.grade_level == session.selected_grade,
                    models.Resource.is_approved == True
                ).limit(5).all()
                
                try:
                    index = int(choice) - 1
                    if 0 <= index < len(resources):
                        resource = resources[index]
                        session.selected_resource_id = resource.id
                        session.menu_level = "resource_options"
                        db.commit()
                        
                        response_message = f"CON {resource.title}:\n1. View Summary\n2. Get SMS Link\n3. Translate\n0. Back"
                    else:
                        response_message = "CON Invalid choice. Try again:\n0. Back"
                except ValueError:
                    response_message = "CON Invalid choice. Try again:\n0. Back"
    
    # Resource options
    elif session.menu_level == "resource_options":
        if len(parts) < 5:
            response_message = f"CON Resource Options:\n1. View Summary\n2. Get SMS Link\n3. Translate\n0. Back"
        else:
            choice = parts[4]
            
            if choice == "0":
                session.menu_level = "browse_resources"
                session.selected_resource_id = None
                db.commit()
                
                # Get resources again
                resources = db.query(models.Resource).filter(
                    models.Resource.subject == session.selected_subject,
                    models.Resource.grade_level == session.selected_grade,
                    models.Resource.is_approved == True
                ).limit(5).all()
                
                if resources:
                    options = "\n".join([f"{i+1}. {r.title}" for i, r in enumerate(resources)])
                    response_message = f"CON Select Resource:\n{options}\n0. Back"
                else:
                    response_message = "CON No resources found.\n0. Back"
            elif choice == "1":
                # View summary
                resource = db.query(models.Resource).filter(
                    models.Resource.id == session.selected_resource_id
                ).first()
                
                if resource:
                    summary = ai_services.summarize_text(resource.description or resource.title)
                    response_message = f"END Summary: {summary}"
                else:
                    response_message = "END Resource not found."
            elif choice == "2":
                # Get SMS link (in a real implementation, this would send an SMS)
                resource = db.query(models.Resource).filter(
                    models.Resource.id == session.selected_resource_id
                ).first()
                
                if resource:
                    # In a real implementation, integrate with SMS gateway
                    response_message = "END SMS with resource link will be sent shortly."
                else:
                    response_message = "END Resource not found."
            elif choice == "3":
                session.menu_level = "select_translation_language"
                db.commit()
                response_message = "CON Select Language:\n1. Swahili\n2. Hausa\n3. Yoruba\n4. Zulu\n5. Amharic\n0. Back"
            else:
                response_message = "CON Invalid choice. Try again:\n1. View Summary\n2. Get SMS Link\n3. Translate\n0. Back"
    
    # Select translation language
    elif session.menu_level == "select_translation_language":
        if len(parts) < 6:
            response_message = "CON Select Language:\n1. Swahili\n2. Hausa\n3. Yoruba\n4. Zulu\n5. Amharic\n0. Back"
        else:
            choice = parts[5]
            language_map = {
                "1": "sw",
                "2": "ha",
                "3": "yo",
                "4": "zu",
                "5": "am"
            }
            
            if choice == "0":
                session.menu_level = "resource_options"
                db.commit()
                response_message = f"CON Resource Options:\n1. View Summary\n2. Get SMS Link\n3. Translate\n0. Back"
            elif choice in language_map:
                target_language = language_map[choice]
                resource = db.query(models.Resource).filter(
                    models.Resource.id == session.selected_resource_id
                ).first()
                
                if resource:
                    translated_title = ai_services.translate_text(
                        resource.title, target_language
                    )
                    response_message = f"END Translated title: {translated_title}"
                else:
                    response_message = "END Resource not found."
            else:
                response_message = "CON Invalid choice. Try again:\n1. Swahili\n2. Hausa\n3. Yoruba\n4. Zulu\n5. Amharic\n0. Back"
    
    # Search resources
    elif session.menu_level == "search":
        if len(parts) < 2:
            response_message = "CON Enter search term:"
        else:
            search_term = parts[1]
            resources = db.query(models.Resource).filter(
                (models.Resource.title.ilike(f"%{search_term}%")) |
                (models.Resource.description.ilike(f"%{search_term}%")) |
                (models.Resource.tags.ilike(f"%{search_term}%")),
                models.Resource.is_approved == True
            ).limit(5).all()
            
            if resources:
                options = "\n".join([f"{i+1}. {r.title} ({r.subject})" for i, r in enumerate(resources)])
                response_message = f"CON Search Results:\n{options}\n0. Back"
                
                # Store the search results in session for later use
                session.menu_level = "search_results"
                db.commit()
            else:
                response_message = "CON No resources found.\n0. Back"
                session.menu_level = "main"
                db.commit()
    
    # Handle search results
    elif session.menu_level == "search_results":
        # Similar to browse_resources handling
        # Implementation would be similar to the browse_resources section
        response_message = "CON Search results functionality would be implemented here.\n0. Back"
    
    # Account management
    elif session.menu_level == "account":
        # Implementation for user registration and login
        response_message = "CON Account management would be implemented here.\n0. Back"
    
    return schemas.USSDResponse(message=response_message)