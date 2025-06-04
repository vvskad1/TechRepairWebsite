from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db import SessionLocal
import crud, schemas

router = APIRouter(prefix="/services", tags=["Services"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=list[schemas.ServiceOut])
def list_services(db: Session = Depends(get_db)):
    return crud.get_services(db)
