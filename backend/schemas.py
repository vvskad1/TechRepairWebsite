from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional, Dict

class BookingCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str
    device: str
    issue: str
    date: datetime

class BookingUpdate(BaseModel):
    status: str

class BookingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: EmailStr
    phone: str
    device: str
    issue: str
    date: datetime
    status: str
    created_at: datetime

class DashboardStats(BaseModel):
    total_bookings: int
    pending_bookings: int
    today_bookings: int
    status_counts: Dict[str, int]

class ServiceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: str
    price: int

class TicketStatusOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    booking_id: int
    status: str
    updated_at: datetime
