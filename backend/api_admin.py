from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db import SessionLocal
from typing import List, Optional
from datetime import datetime
from sqlalchemy import func
import crud, schemas, models

router = APIRouter(prefix="/admin", tags=["Admin"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/bookings", response_model=List[schemas.BookingOut])
async def list_bookings(
    db: Session = Depends(get_db),
    status: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None
):
    """
    Get all bookings with optional filters:
    - status: Filter by booking status (pending, confirmed, completed, cancelled)
    - from_date: Get bookings from this date
    - to_date: Get bookings until this date
    """
    query = db.query(models.Booking)
    
    if status:
        query = query.filter(models.Booking.status == status)
    if from_date:
        query = query.filter(models.Booking.date >= from_date)
    if to_date:
        query = query.filter(models.Booking.date <= to_date)
        
    return query.order_by(models.Booking.date.desc()).all()

@router.get("/bookings/{booking_id}", response_model=schemas.BookingOut)
async def get_booking(booking_id: int, db: Session = Depends(get_db)):
    """Get a specific booking by ID"""
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking

@router.patch("/bookings/{booking_id}", response_model=schemas.BookingOut)
async def update_booking_status(
    booking_id: int,
    status: str,
    db: Session = Depends(get_db)
):
    """Update booking status (pending, confirmed, completed, cancelled)"""
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    valid_statuses = ["pending", "confirmed", "completed", "cancelled"]
    if status not in valid_statuses:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )
    
    booking.status = status
    db.commit()
    db.refresh(booking)
    return booking

@router.get("/dashboard/stats")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics"""
    total_bookings = db.query(models.Booking).count()
    pending_bookings = db.query(models.Booking).filter(
        models.Booking.status == "pending"
    ).count()
    today_bookings = db.query(models.Booking).filter(
        models.Booking.date >= datetime.now().date()
    ).count()
    
    status_counts = {}
    for status in ["pending", "confirmed", "completed", "cancelled"]:
        count = db.query(models.Booking).filter(
            models.Booking.status == status
        ).count()
        status_counts[status] = count
    
    return {
        "total_bookings": total_bookings,
        "pending_bookings": pending_bookings,
        "today_bookings": today_bookings,
        "status_counts": status_counts
    }

@router.get("/dashboard/device-issue-stats")
async def get_device_issue_stats(db: Session = Depends(get_db)):
    """Get stats about number of repairs by device type and issue type."""
    # Device type stats
    device_counts = db.query(models.Booking.device, func.count(models.Booking.id)).group_by(models.Booking.device).all()
    # Issue type stats
    issue_counts = db.query(models.Booking.issue, func.count(models.Booking.id)).group_by(models.Booking.issue).all()
    return {
        "device_counts": [
            {"device": d, "count": c} for d, c in device_counts
        ],
        "issue_counts": [
            {"issue": i, "count": c} for i, c in issue_counts
        ]
    }

@router.delete("/bookings/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_booking(booking_id: int, db: Session = Depends(get_db)):
    """Delete a booking"""
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    db.delete(booking)
    db.commit()
    return {"status": "success"}
