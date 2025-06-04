from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import SessionLocal
import crud, schemas

router = APIRouter(prefix="/ticket", tags=["Ticket"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/{ticket_id}", response_model=schemas.TicketStatusOut)
def get_ticket_status(ticket_id: int, db: Session = Depends(get_db)):
    ticket = crud.get_ticket_status(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket
