from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from db import SessionLocal
from models import Contact
from pydantic import BaseModel
from datetime import datetime
from email_utils import send_email_notification
import os

router = APIRouter(prefix="/contact", tags=["Contact"])

class ContactIn(BaseModel):
    name: str
    email: str
    message: str

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_contact(contact: ContactIn, db: Session = Depends(get_db)):
    db_contact = Contact(
        name=contact.name,
        email=contact.email,
        message=contact.message,
        created_at=datetime.utcnow()
    )
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    # Send email notification to admin
    admin_email = os.getenv("ADMIN_EMAIL", "support@fixittech.com")
    subject = f"New Contact Form Submission from {contact.name}"
    body = f"Name: {contact.name}\nEmail: {contact.email}\nMessage:\n{contact.message}"
    send_email_notification(admin_email, subject, body)
    return {"message": "Contact saved"}
