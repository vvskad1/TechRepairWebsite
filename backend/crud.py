from sqlalchemy.orm import Session
from models import Booking, Service, Ticket
from schemas import BookingCreate
from datetime import datetime

def create_booking(db: Session, booking: BookingCreate) -> Booking:
    db_booking = Booking(
        name=booking.name,
        email=booking.email,
        phone=booking.phone,
        device=booking.device,
        issue=booking.issue,
        date=booking.date,
    )
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking

def get_services(db: Session):
    return db.query(Service).all()

def get_ticket_status(db: Session, ticket_id: int):
    return db.query(Ticket).filter(Ticket.id == ticket_id).first()
